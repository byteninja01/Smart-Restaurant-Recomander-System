# from flask import Flask, render_template, request, jsonify
# import pickle
# import pandas as pd
# import difflib
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import numpy as np

# app = Flask(__name__)

# # Load recommendation model components
# tfidf = pickle.load(open("tfidf.pkl", "rb"))
# cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))
# df_model = pickle.load(open("data.pkl", "rb"))

# # Load data for dashboard
# df_dashboard = pd.read_csv("zomato_processed.csv")

# # Ensure restaurant names mapping is case-insensitive
# df_model['Restaurant_Name_clean'] = df_model['Restaurant_Name'].str.strip()
# indices = pd.Series(df_model.index, index=df_model['Restaurant_Name_clean'].str.lower()).drop_duplicates()

# def recommend_restaurants(restaurant_name, num_recommendations=5):
#     name_clean = restaurant_name.strip().lower()
#     if name_clean not in indices:
#         all_names = list(indices.index)
#         close_matches = difflib.get_close_matches(name_clean, all_names, n=5, cutoff=0.6)
#         return None, close_matches

#     idx = indices[name_clean]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:num_recommendations + 1]
#     restaurant_indices = [i[0] for i in sim_scores]

#     recommended_df = df_model[['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']].iloc[restaurant_indices]
#     return recommended_df, []

# # NEW: Advanced filtering function
# def advanced_search(filters):
#     """
#     Filter restaurants based on multiple criteria:
#     - cuisine_type
#     - min_rating
#     - max_price
#     - locality
#     """
#     filtered_df = df_dashboard.copy()
    
#     if filters.get('cuisine'):
#         filtered_df = filtered_df[filtered_df['Category'].str.contains(filters['cuisine'], case=False, na=False)]
    
#     if filters.get('min_rating'):
#         filtered_df = filtered_df[filtered_df['Dining_Rating'] >= float(filters['min_rating'])]
    
#     if filters.get('max_price'):
#         filtered_df = filtered_df[filtered_df['Pricing_for_2'] <= int(filters['max_price'])]
    
#     if filters.get('locality'):
#         filtered_df = filtered_df[filtered_df['Locality'].str.contains(filters['locality'], case=False, na=False)]
    
#     return filtered_df.sort_values('Dining_Rating', ascending=False).head(20)

# # NEW: Compare restaurants
# def compare_restaurants(rest1, rest2):
#     """Compare two restaurants across multiple dimensions"""
#     name1_clean = rest1.strip().lower()
#     name2_clean = rest2.strip().lower()
    
#     if name1_clean not in indices or name2_clean not in indices:
#         return None
    
#     idx1 = indices[name1_clean]
#     idx2 = indices[name2_clean]
    
#     comparison = {
#         'restaurant1': df_model.iloc[idx1].to_dict(),
#         'restaurant2': df_model.iloc[idx2].to_dict(),
#         'similarity_score': float(cosine_sim[idx1][idx2])
#     }
    
#     return comparison

# # Landing/Intro Page
# @app.route('/')
# def home():
#     return render_template('intro.html')

# # Recommendation Page
# @app.route('/recommend')
# def recommend_page():
#     return render_template('recommend.html')

# # Recommendation Result
# @app.route('/get-recommendations', methods=['POST'])
# def get_recommendations():
#     restaurant_name = request.form.get('restaurant', '')
#     recommendations, suggestions = recommend_restaurants(restaurant_name)

#     if recommendations is None:
#         return render_template('result.html',
#                                error=True,
#                                restaurant_name=restaurant_name,
#                                suggestions=suggestions)
    
#     return render_template('result.html',
#                            error=False,
#                            restaurant_name=restaurant_name,
#                            recommendations=recommendations.values.tolist())

# # NEW: Advanced Search Page
# @app.route('/advanced-search')
# def advanced_search_page():
#     cuisines = sorted(df_dashboard['Category'].dropna().unique())
#     localities = sorted(df_dashboard['Locality'].dropna().unique())
#     return render_template('advanced_search.html', cuisines=cuisines, localities=localities)

# # NEW: Advanced Search Results
# @app.route('/search-results', methods=['POST'])
# def search_results():
#     filters = {
#         'cuisine': request.form.get('cuisine', ''),
#         'min_rating': request.form.get('min_rating', ''),
#         'max_price': request.form.get('max_price', ''),
#         'locality': request.form.get('locality', '')
#     }
    
#     results = advanced_search(filters)
    
#     # Select only the columns we need for display
#     display_columns = ['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']
#     results_to_show = results[display_columns] if len(results) > 0 else results
    
#     return render_template('search_results.html', 
#                          results=results_to_show.values.tolist() if len(results) > 0 else [],
#                          filters=filters,
#                          count=len(results))

# # NEW: Compare Page
# @app.route('/compare')
# def compare_page():
#     return render_template('compare.html')

# # NEW: Compare Results
# @app.route('/compare-results', methods=['POST'])
# def compare_results():
#     rest1 = request.form.get('restaurant1', '')
#     rest2 = request.form.get('restaurant2', '')
    
#     comparison = compare_restaurants(rest1, rest2)
    
#     if comparison is None:
#         return render_template('compare_results.html', error=True)
    
#     return render_template('compare_results.html', 
#                          error=False,
#                          comparison=comparison)

# # NEW: Explore by Cuisine
# @app.route('/explore/<cuisine>')
# def explore_cuisine(cuisine):
#     filtered = df_dashboard[df_dashboard['Category'].str.contains(cuisine, case=False, na=False)]
#     top_restaurants = filtered.sort_values('Dining_Rating', ascending=False).head(15)
    
#     return render_template('explore_cuisine.html',
#                          cuisine=cuisine,
#                          restaurants=top_restaurants.values.tolist())

# # NEW: API endpoint for autocomplete
# @app.route('/api/restaurants')
# def api_restaurants():
#     query = request.args.get('q', '').lower()
#     if len(query) < 2:
#         return jsonify([])
    
#     matches = [name for name in indices.index if query in name][:10]
#     return jsonify(matches)

# # Enhanced Dashboard
# @app.route('/dashboard')
# def dashboard():
#     # Top Cuisine Categories
#     top_categories = df_dashboard['Category'].value_counts().head(10)
#     fig1 = px.bar(
#         x=top_categories.values,
#         y=top_categories.index,
#         orientation='h',
#         title='Top 10 Cuisine Categories',
#         color=top_categories.values,
#         color_continuous_scale='Viridis',
#         labels={'x': 'Number of Restaurants', 'y': 'Cuisine Category'}
#     )
#     fig1.update_layout(showlegend=False, height=500)
#     graph1 = fig1.to_html(full_html=False)

#     # Price vs Dining Rating Scatter with trendline
#     fig2 = px.scatter(
#         df_dashboard, x='Pricing_for_2', y='Dining_Rating',
#         color='Category',
#         title='Price vs Dining Rating Analysis',
#         trendline="ols",
#         hover_data=['Restaurant_Name']
#     )
#     fig2.update_layout(height=500)
#     graph2 = fig2.to_html(full_html=False)

#     # Top Localities by Average Rating
#     locality_rating = df_dashboard.groupby('Locality')['Dining_Rating'].mean().sort_values(ascending=False).head(10)
#     fig3 = px.bar(
#         x=locality_rating.values,
#         y=locality_rating.index,
#         orientation='h',
#         title='Top Localities by Average Dining Rating',
#         color=locality_rating.values,
#         color_continuous_scale='Bluered',
#         labels={'x': 'Average Rating', 'y': 'Locality'}
#     )
#     fig3.update_layout(showlegend=False, height=500)
#     graph3 = fig3.to_html(full_html=False)

#     # Dine-in vs Delivery Comparison
#     ratings = pd.melt(df_dashboard[['Dining_Rating','Delivery_Rating']], var_name='Type', value_name='Rating')
#     fig4 = px.box(
#         ratings, x='Type', y='Rating', color='Type',
#         title='Dining vs Delivery Rating Distribution'
#     )
#     fig4.update_layout(height=500)
#     graph4 = fig4.to_html(full_html=False)

#     # NEW: Price Distribution by Category (top 10 categories only)
#     top_10_categories = df_dashboard['Category'].value_counts().head(10).index
#     df_top_categories = df_dashboard[df_dashboard['Category'].isin(top_10_categories)]
    
#     fig5 = px.violin(
#         df_top_categories, 
#         x='Category', 
#         y='Pricing_for_2',
#         title='Price Distribution Across Top Cuisines',
#         box=True
#     )
#     fig5.update_layout(xaxis_tickangle=-45, height=500)
#     graph5 = fig5.to_html(full_html=False)

#     # Map Visualization
#     fig6 = px.scatter_mapbox(
#         df_dashboard,
#         lat="Latitude",
#         lon="Longitude",
#         color="Dining_Rating",
#         hover_name="Restaurant_Name",
#         hover_data=["Locality", "Category", "Pricing_for_2"],
#         color_continuous_scale="Viridis",
#         zoom=11,
#         height=600
#     )
#     fig6.update_layout(mapbox_style="open-street-map", title="Restaurant Ratings on Map")
#     graph6 = fig6.to_html(full_html=False)

#     # NEW: Key Statistics
#     stats = {
#         'total_restaurants': len(df_dashboard),
#         'avg_dining_rating': round(df_dashboard['Dining_Rating'].mean(), 2),
#         'avg_price': round(df_dashboard['Pricing_for_2'].mean(), 0),
#         'total_cuisines': df_dashboard['Category'].nunique(),
#         'total_localities': df_dashboard['Locality'].nunique()
#     }

#     return render_template(
#         'dashboard.html',
#         graph1=graph1, graph2=graph2, graph3=graph3, 
#         graph4=graph4, graph5=graph5, graph6=graph6,
#         stats=stats
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request, jsonify
# import pickle
# import pandas as pd
# import difflib
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import numpy as np

# app = Flask(__name__)

# # Load recommendation model components
# tfidf = pickle.load(open("tfidf.pkl", "rb"))
# cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))
# df_model = pickle.load(open("data.pkl", "rb"))

# # Load data for dashboard
# df_dashboard = pd.read_csv("zomato_processed.csv")

# # Ensure restaurant names mapping is case-insensitive
# df_model['Restaurant_Name_clean'] = df_model['Restaurant_Name'].str.strip()
# indices = pd.Series(df_model.index, index=df_model['Restaurant_Name_clean'].str.lower()).drop_duplicates()

# def recommend_restaurants(restaurant_name, num_recommendations=5):
#     name_clean = restaurant_name.strip().lower()
#     if name_clean not in indices:
#         all_names = list(indices.index)
#         close_matches = difflib.get_close_matches(name_clean, all_names, n=5, cutoff=0.6)
#         return None, close_matches

#     idx = indices[name_clean]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:num_recommendations + 1]
#     restaurant_indices = [i[0] for i in sim_scores]

#     recommended_df = df_model[['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']].iloc[restaurant_indices]
#     return recommended_df, []

# # NEW: Advanced filtering function
# def advanced_search(filters):
#     """
#     Filter restaurants based on multiple criteria:
#     - cuisine_type
#     - min_rating
#     - max_price
#     - locality
#     """
#     filtered_df = df_dashboard.copy()
    
#     if filters.get('cuisine'):
#         filtered_df = filtered_df[filtered_df['Category'].str.contains(filters['cuisine'], case=False, na=False)]
    
#     if filters.get('min_rating'):
#         filtered_df = filtered_df[filtered_df['Dining_Rating'] >= float(filters['min_rating'])]
    
#     if filters.get('max_price'):
#         filtered_df = filtered_df[filtered_df['Pricing_for_2'] <= int(filters['max_price'])]
    
#     if filters.get('locality'):
#         filtered_df = filtered_df[filtered_df['Locality'].str.contains(filters['locality'], case=False, na=False)]
    
#     return filtered_df.sort_values('Dining_Rating', ascending=False).head(20)

# # NEW: Compare restaurants
# def compare_restaurants(rest1, rest2):
#     """Compare two restaurants across multiple dimensions"""
#     name1_clean = rest1.strip().lower()
#     name2_clean = rest2.strip().lower()
    
#     if name1_clean not in indices or name2_clean not in indices:
#         return None
    
#     idx1 = indices[name1_clean]
#     idx2 = indices[name2_clean]
    
#     comparison = {
#         'restaurant1': df_model.iloc[idx1].to_dict(),
#         'restaurant2': df_model.iloc[idx2].to_dict(),
#         'similarity_score': float(cosine_sim[idx1][idx2])
#     }
    
#     return comparison

# # Landing/Intro Page
# @app.route('/')
# def home():
#     return render_template('intro.html')

# # Recommendation Page
# @app.route('/recommend')
# def recommend_page():
#     return render_template('recommend.html')

# # Recommendation Result
# @app.route('/get-recommendations', methods=['POST'])
# def get_recommendations():
#     restaurant_name = request.form.get('restaurant', '')
#     recommendations, suggestions = recommend_restaurants(restaurant_name)

#     if recommendations is None:
#         return render_template('result.html',
#                                error=True,
#                                restaurant_name=restaurant_name,
#                                suggestions=suggestions)
    
#     return render_template('result.html',
#                            error=False,
#                            restaurant_name=restaurant_name,
#                            recommendations=recommendations.values.tolist())

# # NEW: Advanced Search Page
# @app.route('/advanced-search')
# def advanced_search_page():
#     cuisines = sorted(df_dashboard['Category'].dropna().unique())
#     localities = sorted(df_dashboard['Locality'].dropna().unique())
#     return render_template('advanced_search.html', cuisines=cuisines, localities=localities)

# # NEW: Advanced Search Results
# @app.route('/search-results', methods=['POST'])
# def search_results():
#     filters = {
#         'cuisine': request.form.get('cuisine', ''),
#         'min_rating': request.form.get('min_rating', ''),
#         'max_price': request.form.get('max_price', ''),
#         'locality': request.form.get('locality', '')
#     }
    
#     results = advanced_search(filters)
    
#     # Select only the columns we need for display
#     display_columns = ['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']
#     results_to_show = results[display_columns] if len(results) > 0 else results
    
#     return render_template('search_results.html', 
#                          results=results_to_show.values.tolist() if len(results) > 0 else [],
#                          filters=filters,
#                          count=len(results))

# # NEW: Compare Page
# @app.route('/compare')
# def compare_page():
#     return render_template('compare.html')

# # NEW: Compare Results
# @app.route('/compare-results', methods=['POST'])
# def compare_results():
#     rest1 = request.form.get('restaurant1', '')
#     rest2 = request.form.get('restaurant2', '')
    
#     comparison = compare_restaurants(rest1, rest2)
    
#     if comparison is None:
#         return render_template('compare_results.html', error=True)
    
#     return render_template('compare_results.html', 
#                          error=False,
#                          comparison=comparison)

# # NEW: Explore by Cuisine
# @app.route('/explore/<cuisine>')
# def explore_cuisine(cuisine):
#     filtered = df_dashboard[df_dashboard['Category'].str.contains(cuisine, case=False, na=False)]
#     top_restaurants = filtered.sort_values('Dining_Rating', ascending=False).head(15)
    
#     return render_template('explore_cuisine.html',
#                          cuisine=cuisine,
#                          restaurants=top_restaurants.values.tolist())

# # NEW: API endpoint for autocomplete
# @app.route('/api/restaurants')
# def api_restaurants():
#     query = request.args.get('q', '').lower()
#     if len(query) < 2:
#         return jsonify([])
    
#     matches = [name for name in indices.index if query in name][:10]
#     return jsonify(matches)

# # Enhanced Dashboard
# @app.route('/dashboard')
# def dashboard():
#     # Top Cuisine Categories
#     top_categories = df_dashboard['Category'].value_counts().head(10)
#     fig1 = px.bar(
#         x=top_categories.values,
#         y=top_categories.index,
#         orientation='h',
#         title='Top 10 Cuisine Categories',
#         color=top_categories.values,
#         color_continuous_scale='Viridis',
#         labels={'x': 'Number of Restaurants', 'y': 'Cuisine Category'}
#     )
#     fig1.update_layout(showlegend=False, height=500)
#     graph1 = fig1.to_html(full_html=False)

#     # Price vs Dining Rating Scatter
#     fig2 = px.scatter(
#         df_dashboard, x='Pricing_for_2', y='Dining_Rating',
#         color='Category',
#         title='Price vs Dining Rating Analysis',
#         hover_data=['Restaurant_Name']
#     )
#     fig2.update_layout(height=500)
#     graph2 = fig2.to_html(full_html=False)

#     # Top Localities by Average Rating
#     locality_rating = df_dashboard.groupby('Locality')['Dining_Rating'].mean().sort_values(ascending=False).head(10)
#     fig3 = px.bar(
#         x=locality_rating.values,
#         y=locality_rating.index,
#         orientation='h',
#         title='Top Localities by Average Dining Rating',
#         color=locality_rating.values,
#         color_continuous_scale='Bluered',
#         labels={'x': 'Average Rating', 'y': 'Locality'}
#     )
#     fig3.update_layout(showlegend=False, height=500)
#     graph3 = fig3.to_html(full_html=False)

#     # Dine-in vs Delivery Comparison
#     ratings = pd.melt(df_dashboard[['Dining_Rating','Delivery_Rating']], var_name='Type', value_name='Rating')
#     fig4 = px.box(
#         ratings, x='Type', y='Rating', color='Type',
#         title='Dining vs Delivery Rating Distribution'
#     )
#     fig4.update_layout(height=500)
#     graph4 = fig4.to_html(full_html=False)

#     # NEW: Price Distribution by Category (top 10 categories only)
#     top_10_categories = df_dashboard['Category'].value_counts().head(10).index
#     df_top_categories = df_dashboard[df_dashboard['Category'].isin(top_10_categories)]
    
#     fig5 = px.violin(
#         df_top_categories, 
#         x='Category', 
#         y='Pricing_for_2',
#         title='Price Distribution Across Top Cuisines',
#         box=True
#     )
#     fig5.update_layout(xaxis_tickangle=-45, height=500)
#     graph5 = fig5.to_html(full_html=False)

#     # Map Visualization
#     fig6 = px.scatter_mapbox(
#         df_dashboard,
#         lat="Latitude",
#         lon="Longitude",
#         color="Dining_Rating",
#         hover_name="Restaurant_Name",
#         hover_data=["Locality", "Category", "Pricing_for_2"],
#         color_continuous_scale="Viridis",
#         zoom=11,
#         height=600
#     )
#     fig6.update_layout(mapbox_style="open-street-map", title="Restaurant Ratings on Map")
#     graph6 = fig6.to_html(full_html=False)

#     # NEW: Key Statistics
#     stats = {
#         'total_restaurants': len(df_dashboard),
#         'avg_dining_rating': round(df_dashboard['Dining_Rating'].mean(), 2),
#         'avg_price': round(df_dashboard['Pricing_for_2'].mean(), 0),
#         'total_cuisines': df_dashboard['Category'].nunique(),
#         'total_localities': df_dashboard['Locality'].nunique()
#     }

#     return render_template(
#         'dashboard.html',
#         graph1=graph1, graph2=graph2, graph3=graph3, 
#         graph4=graph4, graph5=graph5, graph6=graph6,
#         stats=stats
#     )

# if __name__ == '__main__':
#     app.run(debug=True)
# from flask import Flask, render_template, request, jsonify
# import pickle
# import pandas as pd
# import difflib
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import numpy as np

# app = Flask(__name__)

# # Load recommendation model components
# tfidf = pickle.load(open("tfidf.pkl", "rb"))
# cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))
# df_model = pickle.load(open("data.pkl", "rb"))

# # Load data for dashboard
# df_dashboard = pd.read_csv("zomato_processed.csv")

# # Ensure restaurant names mapping is case-insensitive
# df_model['Restaurant_Name_clean'] = df_model['Restaurant_Name'].str.strip()
# indices = pd.Series(df_model.index, index=df_model['Restaurant_Name_clean'].str.lower()).drop_duplicates()

# def recommend_restaurants(restaurant_name, num_recommendations=5):
#     name_clean = restaurant_name.strip().lower()
#     if name_clean not in indices:
#         all_names = list(indices.index)
#         close_matches = difflib.get_close_matches(name_clean, all_names, n=5, cutoff=0.6)
#         return None, close_matches

#     idx = indices[name_clean]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:num_recommendations + 1]
#     restaurant_indices = [i[0] for i in sim_scores]

#     recommended_df = df_model[['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']].iloc[restaurant_indices]
#     return recommended_df, []

# def advanced_search(filters):
#     """
#     Filter restaurants based on multiple criteria:
#     - cuisine_type
#     - min_rating
#     - max_price
#     - locality
#     """
#     filtered_df = df_dashboard.copy()
    
#     if filters.get('cuisine'):
#         filtered_df = filtered_df[filtered_df['Category'].str.contains(filters['cuisine'], case=False, na=False)]
    
#     if filters.get('min_rating'):
#         filtered_df = filtered_df[filtered_df['Dining_Rating'] >= float(filters['min_rating'])]
    
#     if filters.get('max_price'):
#         filtered_df = filtered_df[filtered_df['Pricing_for_2'] <= int(filters['max_price'])]
    
#     if filters.get('locality'):
#         filtered_df = filtered_df[filtered_df['Locality'].str.contains(filters['locality'], case=False, na=False)]
    
#     return filtered_df.sort_values('Dining_Rating', ascending=False).head(20)

# def compare_restaurants(rest1, rest2):
#     """Compare two restaurants across multiple dimensions"""
#     name1_clean = rest1.strip().lower()
#     name2_clean = rest2.strip().lower()
    
#     if name1_clean not in indices or name2_clean not in indices:
#         return None
    
#     idx1 = indices[name1_clean]
#     idx2 = indices[name2_clean]
    
#     # Get restaurant data as dictionaries
#     rest1_data = df_model.iloc[idx1].to_dict()
#     rest2_data = df_model.iloc[idx2].to_dict()
    
#     comparison = {
#         'restaurant1': rest1_data,
#         'restaurant2': rest2_data,
#         'similarity_score': float(cosine_sim[idx1][idx2])
#     }
    
#     return comparison

# # Landing/Intro Page
# @app.route('/')
# def home():
#     return render_template('intro.html')

# # Recommendation Page
# @app.route('/recommend')
# def recommend_page():
#     return render_template('recommend.html')

# # Recommendation Result
# @app.route('/get-recommendations', methods=['POST'])
# def get_recommendations():
#     restaurant_name = request.form.get('restaurant', '')
#     recommendations, suggestions = recommend_restaurants(restaurant_name)

#     if recommendations is None:
#         return render_template('result.html',
#                                error=True,
#                                restaurant_name=restaurant_name,
#                                suggestions=suggestions)
    
#     return render_template('result.html',
#                            error=False,
#                            restaurant_name=restaurant_name,
#                            recommendations=recommendations.values.tolist())

# # Advanced Search Page
# @app.route('/advanced-search')
# def advanced_search_page():
#     cuisines = sorted(df_dashboard['Category'].dropna().unique())
#     localities = sorted(df_dashboard['Locality'].dropna().unique())
#     return render_template('advanced_search.html', cuisines=cuisines, localities=localities)

# # Advanced Search Results
# @app.route('/search-results', methods=['POST'])
# def search_results():
#     filters = {
#         'cuisine': request.form.get('cuisine', ''),
#         'min_rating': request.form.get('min_rating', ''),
#         'max_price': request.form.get('max_price', ''),
#         'locality': request.form.get('locality', '')
#     }
    
#     results = advanced_search(filters)
    
#     # Select only the columns we need for display
#     display_columns = ['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']
#     results_to_show = results[display_columns] if len(results) > 0 else results
    
#     return render_template('search_results.html', 
#                          results=results_to_show.values.tolist() if len(results) > 0 else [],
#                          filters=filters,
#                          count=len(results))

# # Compare Page
# @app.route('/compare')
# def compare_page():
#     return render_template('compare.html')

# # Compare Results
# @app.route('/compare-results', methods=['POST'])
# def compare_results():
#     rest1 = request.form.get('restaurant1', '')
#     rest2 = request.form.get('restaurant2', '')
    
#     comparison = compare_restaurants(rest1, rest2)
    
#     if comparison is None:
#         return render_template('compare_results.html', error=True)
    
#     return render_template('compare_results.html', 
#                          error=False,
#                          comparison=comparison)

# # Explore by Cuisine
# @app.route('/explore/<cuisine>')
# def explore_cuisine(cuisine):
#     filtered = df_dashboard[df_dashboard['Category'].str.contains(cuisine, case=False, na=False)]
#     top_restaurants = filtered.sort_values('Dining_Rating', ascending=False).head(15)
    
#     return render_template('explore_cuisine.html',
#                          cuisine=cuisine,
#                          restaurants=top_restaurants.values.tolist())

# # API endpoint for autocomplete
# @app.route('/api/restaurants')
# def api_restaurants():
#     query = request.args.get('q', '').lower()
#     if len(query) < 2:
#         return jsonify([])
    
#     matches = [name for name in indices.index if query in name][:10]
#     return jsonify(matches)

# # Enhanced Dashboard
# @app.route('/dashboard')
# def dashboard():
#     # Top Cuisine Categories
#     top_categories = df_dashboard['Category'].value_counts().head(10)
#     fig1 = px.bar(
#         x=top_categories.values,
#         y=top_categories.index,
#         orientation='h',
#         title='Top 10 Cuisine Categories',
#         color=top_categories.values,
#         color_continuous_scale='Viridis',
#         labels={'x': 'Number of Restaurants', 'y': 'Cuisine Category'}
#     )
#     fig1.update_layout(showlegend=False, height=500)
#     graph1 = fig1.to_html(full_html=False)

#     # Price vs Dining Rating Scatter
#     fig2 = px.scatter(
#         df_dashboard, x='Pricing_for_2', y='Dining_Rating',
#         color='Category',
#         title='Price vs Dining Rating Analysis',
#         hover_data=['Restaurant_Name']
#     )
#     fig2.update_layout(height=500)
#     graph2 = fig2.to_html(full_html=False)

#     # Top Localities by Average Rating
#     locality_rating = df_dashboard.groupby('Locality')['Dining_Rating'].mean().sort_values(ascending=False).head(10)
#     fig3 = px.bar(
#         x=locality_rating.values,
#         y=locality_rating.index,
#         orientation='h',
#         title='Top Localities by Average Dining Rating',
#         color=locality_rating.values,
#         color_continuous_scale='Bluered',
#         labels={'x': 'Average Rating', 'y': 'Locality'}
#     )
#     fig3.update_layout(showlegend=False, height=500)
#     graph3 = fig3.to_html(full_html=False)

#     # Dine-in vs Delivery Comparison
#     ratings = pd.melt(df_dashboard[['Dining_Rating','Delivery_Rating']], var_name='Type', value_name='Rating')
#     fig4 = px.box(
#         ratings, x='Type', y='Rating', color='Type',
#         title='Dining vs Delivery Rating Distribution'
#     )
#     fig4.update_layout(height=500)
#     graph4 = fig4.to_html(full_html=False)

#     # Price Distribution by Category (top 10 categories only)
#     top_10_categories = df_dashboard['Category'].value_counts().head(10).index
#     df_top_categories = df_dashboard[df_dashboard['Category'].isin(top_10_categories)]
    
#     fig5 = px.violin(
#         df_top_categories, 
#         x='Category', 
#         y='Pricing_for_2',
#         title='Price Distribution Across Top Cuisines',
#         box=True
#     )
#     fig5.update_layout(xaxis_tickangle=-45, height=500)
#     graph5 = fig5.to_html(full_html=False)

#     # Map Visualization
#     fig6 = px.scatter_mapbox(
#         df_dashboard,
#         lat="Latitude",
#         lon="Longitude",
#         color="Dining_Rating",
#         hover_name="Restaurant_Name",
#         hover_data=["Locality", "Category", "Pricing_for_2"],
#         color_continuous_scale="Viridis",
#         zoom=11,
#         height=600
#     )
#     fig6.update_layout(mapbox_style="open-street-map", title="Restaurant Ratings on Map")
#     graph6 = fig6.to_html(full_html=False)

#     # Key Statistics
#     stats = {
#         'total_restaurants': len(df_dashboard),
#         'avg_dining_rating': round(df_dashboard['Dining_Rating'].mean(), 2),
#         'avg_price': round(df_dashboard['Pricing_for_2'].mean(), 0),
#         'total_cuisines': df_dashboard['Category'].nunique(),
#         'total_localities': df_dashboard['Locality'].nunique()
#     }

#     return render_template(
#         'dashboard.html',
#         graph1=graph1, graph2=graph2, graph3=graph3, 
#         graph4=graph4, graph5=graph5, graph6=graph6,
#         stats=stats
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import difflib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

app = Flask(__name__)

# Load recommendation model components
tfidf = pickle.load(open("tfidf.pkl", "rb"))
cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))
df_model = pickle.load(open("data.pkl", "rb"))

# Load data for dashboard
df_dashboard = pd.read_csv("zomato_processed.csv")

# Ensure restaurant names mapping is case-insensitive
df_model['Restaurant_Name_clean'] = df_model['Restaurant_Name'].str.strip()
indices = pd.Series(df_model.index, index=df_model['Restaurant_Name_clean'].str.lower()).drop_duplicates()

def recommend_restaurants(restaurant_name, num_recommendations=5):
    name_clean = restaurant_name.strip().lower()
    if name_clean not in indices:
        all_names = list(indices.index)
        close_matches = difflib.get_close_matches(name_clean, all_names, n=5, cutoff=0.6)
        return None, close_matches

    idx = indices[name_clean]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations + 1]
    restaurant_indices = [i[0] for i in sim_scores]

    recommended_df = df_model[['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']].iloc[restaurant_indices]
    return recommended_df, []

def advanced_search(filters):
    """
    Filter restaurants based on multiple criteria:
    - cuisine_type
    - min_rating
    - max_price
    - locality
    """
    filtered_df = df_dashboard.copy()
    
    if filters.get('cuisine'):
        filtered_df = filtered_df[filtered_df['Category'].str.contains(filters['cuisine'], case=False, na=False)]
    
    if filters.get('min_rating'):
        filtered_df = filtered_df[filtered_df['Dining_Rating'] >= float(filters['min_rating'])]
    
    if filters.get('max_price'):
        filtered_df = filtered_df[filtered_df['Pricing_for_2'] <= int(filters['max_price'])]
    
    if filters.get('locality'):
        filtered_df = filtered_df[filtered_df['Locality'].str.contains(filters['locality'], case=False, na=False)]
    
    return filtered_df.sort_values('Dining_Rating', ascending=False).head(20)

def compare_restaurants(rest1, rest2):
    """Compare two restaurants across multiple dimensions"""
    name1_clean = rest1.strip().lower()
    name2_clean = rest2.strip().lower()
    
    print(f"\n=== COMPARISON DEBUG ===")
    print(f"Input 1: '{rest1}' -> Cleaned: '{name1_clean}'")
    print(f"Input 2: '{rest2}' -> Cleaned: '{name2_clean}'")
    
    # Check if restaurants exist
    if name1_clean not in indices:
        print(f"Restaurant 1 '{rest1}' NOT FOUND in indices")
        # Try fuzzy matching
        all_names = list(indices.index)
        close_matches = difflib.get_close_matches(name1_clean, all_names, n=1, cutoff=0.8)
        if close_matches:
            print(f"Did you mean: {close_matches[0]}?")
        return None
    
    if name2_clean not in indices:
        print(f"Restaurant 2 '{rest2}' NOT FOUND in indices")
        # Try fuzzy matching
        all_names = list(indices.index)
        close_matches = difflib.get_close_matches(name2_clean, all_names, n=1, cutoff=0.8)
        if close_matches:
            print(f"Did you mean: {close_matches[0]}?")
        return None
    
    idx1 = indices[name1_clean]
    idx2 = indices[name2_clean]
    
    print(f"Found Restaurant 1 at index: {idx1}")
    print(f"Found Restaurant 2 at index: {idx2}")
    
    # Get restaurant data as dictionaries
    rest1_data = df_model.iloc[idx1].to_dict()
    rest2_data = df_model.iloc[idx2].to_dict()
    
    # Calculate similarity score
    similarity = float(cosine_sim[idx1][idx2])
    
    comparison = {
        'restaurant1': rest1_data,
        'restaurant2': rest2_data,
        'similarity_score': similarity,
        'input_name1': rest1,
        'input_name2': rest2
    }
    
    print(f"\nActual Restaurant 1: {rest1_data['Restaurant_Name']}")
    print(f"Actual Restaurant 2: {rest2_data['Restaurant_Name']}")
    print(f"Similarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
    print(f"=== END DEBUG ===\n")
    
    return comparison

# Landing/Intro Page
@app.route('/')
def home():
    return render_template('intro.html')

# Recommendation Page
@app.route('/recommend')
def recommend_page():
    return render_template('recommend.html')

# Recommendation Result
@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    restaurant_name = request.form.get('restaurant', '')
    recommendations, suggestions = recommend_restaurants(restaurant_name)

    if recommendations is None:
        return render_template('result.html',
                               error=True,
                               restaurant_name=restaurant_name,
                               suggestions=suggestions)
    
    return render_template('result.html',
                           error=False,
                           restaurant_name=restaurant_name,
                           recommendations=recommendations.values.tolist())

# Advanced Search Page
@app.route('/advanced-search')
def advanced_search_page():
    cuisines = sorted(df_dashboard['Category'].dropna().unique())
    localities = sorted(df_dashboard['Locality'].dropna().unique())
    return render_template('advanced_search.html', cuisines=cuisines, localities=localities)

# Advanced Search Results
@app.route('/search-results', methods=['POST'])
def search_results():
    filters = {
        'cuisine': request.form.get('cuisine', ''),
        'min_rating': request.form.get('min_rating', ''),
        'max_price': request.form.get('max_price', ''),
        'locality': request.form.get('locality', '')
    }
    
    results = advanced_search(filters)
    
    # Select only the columns we need for display
    display_columns = ['Restaurant_Name', 'Category', 'Locality', 'Pricing_for_2', 'Dining_Rating']
    results_to_show = results[display_columns] if len(results) > 0 else results
    
    return render_template('search_results.html', 
                         results=results_to_show.values.tolist() if len(results) > 0 else [],
                         filters=filters,
                         count=len(results))

# Compare Page
@app.route('/compare')
def compare_page():
    return render_template('compare.html')

# Compare Results
@app.route('/compare-results', methods=['POST'])
def compare_results():
    rest1 = request.form.get('restaurant1', '')
    rest2 = request.form.get('restaurant2', '')
    
    comparison = compare_restaurants(rest1, rest2)
    
    if comparison is None:
        return render_template('compare_results.html', error=True)
    
    return render_template('compare_results.html', 
                         error=False,
                         comparison=comparison)

# Explore by Cuisine
@app.route('/explore/<cuisine>')
def explore_cuisine(cuisine):
    filtered = df_dashboard[df_dashboard['Category'].str.contains(cuisine, case=False, na=False)]
    top_restaurants = filtered.sort_values('Dining_Rating', ascending=False).head(15)
    
    return render_template('explore_cuisine.html',
                         cuisine=cuisine,
                         restaurants=top_restaurants.values.tolist())

# API endpoint for autocomplete
@app.route('/api/restaurants')
def api_restaurants():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    matches = [name for name in indices.index if query in name][:10]
    return jsonify(matches)

# Enhanced Dashboard
@app.route('/dashboard')
def dashboard():
    # Top Cuisine Categories
    top_categories = df_dashboard['Category'].value_counts().head(10)
    fig1 = px.bar(
        x=top_categories.values,
        y=top_categories.index,
        orientation='h',
        title='Top 10 Cuisine Categories',
        color=top_categories.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Number of Restaurants', 'y': 'Cuisine Category'}
    )
    fig1.update_layout(showlegend=False, height=500)
    graph1 = fig1.to_html(full_html=False)

    # Price vs Dining Rating Scatter
    fig2 = px.scatter(
        df_dashboard, x='Pricing_for_2', y='Dining_Rating',
        color='Category',
        title='Price vs Dining Rating Analysis',
        hover_data=['Restaurant_Name']
    )
    fig2.update_layout(height=500)
    graph2 = fig2.to_html(full_html=False)

    # Top Localities by Average Rating
    locality_rating = df_dashboard.groupby('Locality')['Dining_Rating'].mean().sort_values(ascending=False).head(10)
    fig3 = px.bar(
        x=locality_rating.values,
        y=locality_rating.index,
        orientation='h',
        title='Top Localities by Average Dining Rating',
        color=locality_rating.values,
        color_continuous_scale='Bluered',
        labels={'x': 'Average Rating', 'y': 'Locality'}
    )
    fig3.update_layout(showlegend=False, height=500)
    graph3 = fig3.to_html(full_html=False)

    # Dine-in vs Delivery Comparison
    ratings = pd.melt(df_dashboard[['Dining_Rating','Delivery_Rating']], var_name='Type', value_name='Rating')
    fig4 = px.box(
        ratings, x='Type', y='Rating', color='Type',
        title='Dining vs Delivery Rating Distribution'
    )
    fig4.update_layout(height=500)
    graph4 = fig4.to_html(full_html=False)

    # Price Distribution by Category (top 10 categories only)
    top_10_categories = df_dashboard['Category'].value_counts().head(10).index
    df_top_categories = df_dashboard[df_dashboard['Category'].isin(top_10_categories)]
    
    fig5 = px.violin(
        df_top_categories, 
        x='Category', 
        y='Pricing_for_2',
        title='Price Distribution Across Top Cuisines',
        box=True
    )
    fig5.update_layout(xaxis_tickangle=-45, height=500)
    graph5 = fig5.to_html(full_html=False)

    # Map Visualization
    fig6 = px.scatter_mapbox(
        df_dashboard,
        lat="Latitude",
        lon="Longitude",
        color="Dining_Rating",
        hover_name="Restaurant_Name",
        hover_data=["Locality", "Category", "Pricing_for_2"],
        color_continuous_scale="Viridis",
        zoom=11,
        height=600
    )
    fig6.update_layout(mapbox_style="open-street-map", title="Restaurant Ratings on Map")
    graph6 = fig6.to_html(full_html=False)

    # Key Statistics
    stats = {
        'total_restaurants': len(df_dashboard),
        'avg_dining_rating': round(df_dashboard['Dining_Rating'].mean(), 2),
        'avg_price': round(df_dashboard['Pricing_for_2'].mean(), 0),
        'total_cuisines': df_dashboard['Category'].nunique(),
        'total_localities': df_dashboard['Locality'].nunique()
    }

    return render_template(
        'dashboard.html',
        graph1=graph1, graph2=graph2, graph3=graph3, 
        graph4=graph4, graph5=graph5, graph6=graph6,
        stats=stats
    )

if __name__ == '__main__':
    app.run(debug=True)