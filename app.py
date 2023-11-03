# app.py
import streamlit as st
import pandas as pd
from services import calculate_funnel_user_counts, compute_avg_time_by_average_user, plot_avg_time_by_user, \
    plot_heatmap_avg_time_by_user, plot_time_spent_by_users, prepare_data_for_pivot, \
    plot_average_duration_with_trendlines, plot_common_user_journeys, show_exit_rates, \
    plot_interactions_before_exit, plot_daily_interactions, plot_interactions_heatmap, \
    plot_exit_pages_bar_chart, plot_exit_rate_over_time, show_top_user_paths, show_average_duration_by_page, \
    calculate_and_display_bounce_rates, plot_daily_bounce_rates, show_loyal_users

# Load dataset (for illustration purposes)
data = pd.read_csv('data/data_set_da_test.csv')

# Call the function to get funnel data
funnel_data = calculate_funnel_user_counts(data)

# Compute the average duration across all users by page_type
avg_time_by_user = compute_avg_time_by_average_user(data)

st.title('User Funnel Analysis')
st.write("Hello, this app was designed to showcase some of the visuals that have been made as part of"
         "the data analysis part! This app is the demo version. The graphics and chars are customizable and can be "
         "executed with rich UI components like selectors, dropdowns, etc. For demo purposes, the app is limited to "
         "basic functionality. Existing BI platforms were skipped as there might not be an optimal solution for some "
         "visualizations or underlining circumstances.")

st.table(funnel_data)

st.header('Average Time on Page', divider='rainbow')
# st.table(avg_time_by_user.reset_index().rename(columns={0: 'Average Duration (minutes)'}))
# Plot the avt duration per page
plot_avg_time_by_user(avg_time_by_user)

avg_time_by_user = avg_time_by_user.rename(columns={0: 'duration'})
avg_time_by_user['event_day'] = pd.to_datetime(avg_time_by_user['event_day'])
# Removing the remove the time part
avg_time_by_user['event_day'] = avg_time_by_user['event_day'].dt.date
plot_heatmap_avg_time_by_user(avg_time_by_user)

# Display where users spent the most time
plot_time_spent_by_users(avg_time_by_user)

st.subheader(':blue[Trendlines]')
avg_duration_df = prepare_data_for_pivot(avg_time_by_user)
fig_trendlines = plot_average_duration_with_trendlines(avg_duration_df)
st.pyplot(fig_trendlines)

st.subheader(':blue[User Journeys]')
st.write('This would require a more detailed dataset with sequence data. However, for a rudimentary view we can build \
        some daemo viz')
fig_user_journeys = plot_common_user_journeys(data)
st.pyplot(fig_user_journeys)

st.header('Exit Rate', divider='rainbow')
st.write('Exit Rate metric provides insights into the percentage of users who leave the site from a specific page.')
show_exit_rates(data)

markdown_content = """
    **Let's interpret the outcomes of the exit rates for each page:**

    1. **Listing Page (68.26%)**: - For approximately 68.26% of the visits to the listing page, users exit the 
    website from this page. This means the listing page is the last page they view before leaving the site in 68.26% 
    of sessions where the listing page was visited.

    2. **Order Page (11.81%)**: - Only 11.81% of the visits to the order page result in users exiting from this page. 
    This is a good sign as it indicates that a majority of users who reach the order page likely complete their 
    purchase rather than exiting.

    3. **Product Page (53.25%)**: - 53.25% of the time, after users view a product's details on the product page, 
    they exit the website. This might indicate that users are not finding the product details or pricing compelling 
    enough to proceed further more than half the time.

    4. **Search Listing Page (26.83%)**: - When users land on the search listing page, they exit the website 26.83% 
    of the time. This means that in roughly one-fourth of the sessions where users visit the search listing page, 
    they leave the website without proceeding further.

    **Overall Insights**: - The **Listing Page** has the highest exit rate. This might suggest that users are not 
    finding the products they want or are not enticed to click on individual products to view more details. It could 
    be beneficial to investigate the product listings, the layout, and the user experience on this page.

    - The **Order Page** has a low exit rate, which is promising. It suggests that once users are ready to finalize 
    their purchase, they are less likely to abandon the process. This indicates a potentially smooth and 
    user-friendly checkout process.

    - The **Product Page** has a significant exit rate, indicating potential areas of improvement. Understanding user 
    feedback or enhancing product descriptions and visuals might help in retaining users.

    - The **Search Listing Page** has a moderate exit rate. Enhancements to search algorithms, displaying more 
    relevant products, or improving search UI might further reduce this exit rate.

    Exit rates are important as they provide insights into potential areas of friction or user dissatisfaction on 
    different pages. By addressing the issues on pages with high exit rates, businesses can enhance user experience 
    and potentially increase conversions."""
st.markdown(markdown_content)

st.subheader(':blue[Histogram of Products]')
st.write('This will show the distribution of products added to the cart. The most frequently added products will '
         'stand out, indicating their popularity.')
plot_interactions_before_exit(data)

st.subheader(':blue[Time Series Analysis]')
st.write('We can plot the number of "add to cart" actions over time (e.g., by day or hour) to identify any patterns '
         'or trends. This can show if there are specific times when users are more active or if there are dips that '
         'need attention.')
plot_daily_interactions(data)

st.subheader(':blue[Heatmap of Add-to-Cart Actions by Day of Week and Hour]')
st.write('This will help visualize if there are specific times of the day or specific days of the week when users are '
         'more likely to add items to their cart.')
plot_interactions_heatmap(data)

st.subheader(':blue[Exit Page Distribution]')
st.write('A bar chart to show the distribution of exit pages. This helps to identify which pages are most frequently '
         'the last page users visit.')
plot_exit_pages_bar_chart(data)

st.subheader(':blue[Exit Rate Over Time]')
st.write('Observe if there are specific days or time periods when the exit rate spikes. This might correlate with '
         'website changes, marketing campaigns, or external factors.')
plot_exit_rate_over_time(data)

# Page Interactions
st.header('Page Interactions', divider='rainbow')
st.subheader(':blue[Count of common paths]')
show_top_user_paths(data)

# Average Session Duration
st.header('Average Session Duration', divider='rainbow')
st.subheader(':blue[Content Relevance]')
st.write('To gauge content relevance, well analyze the average session duration based on the page_type. This will '
         'give insights into which sections of the platform users spend the most time on, indicating content '
         'relevance and engagement.')
show_average_duration_by_page(data)

markdown_content = """The table above showcases the average duration (in seconds) that users spend on different types 
of pages on the platform. Let's break down the outcome:

1. **Listing Page (`listing_page`):** - Average Duration: Approximately 312.53 seconds (or about 5.21 minutes) - 
Interpretation: Users spend a little over 5 minutes on average when they are on a general listing of products. This 
might be the time taken to skim through various products or decide which one to click on for more details.

2. **Order Page (`order_page`):** - Average Duration: Approximately 995.32 seconds (or about 16.59 minutes) - 
Interpretation: The order page, where users finalize their purchase, has a longer average duration. This suggests 
users spend a significant amount of time here, possibly reviewing their cart, entering payment/shipping details, 
or contemplating their purchase.

3. **Product Page (`product_page`):** - Average Duration: Approximately 547.08 seconds (or about 9.12 minutes) - 
Interpretation: Users spend on average about 9 minutes on product detail pages. They might be reading product 
descriptions, reviews, checking images, or comparing product features.

4. **Search Listing Page (`search_listing_page`):** - Average Duration: Approximately 1201.19 seconds (or about 
20.02 minutes) - Interpretation: This is the page where users can search and see a list of products. The high average 
duration suggests users might be spending a lot of time refining searches, scrolling through many products, 
or perhaps facing difficulty in finding the exact product they're looking for.

**Key Insights:**

- The **Search Listing Page** has the highest average duration, which might suggest that users are taking their time 
to find the right product or that they might be facing challenges in locating their desired items. - The **Order 
Page** also has a significant duration, suggesting the purchase process might be comprehensive or users are being 
cautious before finalizing their orders. - **Product Pages** and **Listing Pages** have relatively shorter durations 
compared to the other two, but they still represent significant user engagement.

From a business perspective, understanding these durations can help in:

- Identifying opportunities to improve user experience (e.g., streamlining the checkout process if the order page 
duration is deemed too long). - Enhancing content on pages where users spend more time. - Investigating any potential 
challenges or obstacles users might be facing on pages with longer durations.

In essence, these insights can guide optimizations to make the user journey smoother and potentially increase 
conversions."""
st.markdown(markdown_content)

# Bounce Rate
st.header('Bounce Rate', divider='rainbow')
st.subheader(':blue[Page-Specific Bounce Rates]')
calculate_and_display_bounce_rates(data)
markdown_content = """
**Detailed Breakdown:**

1. **Listing Page**: - Total Sessions: 180,930 - Bounced Sessions: 138,601 - Bounce Rate: 76.60% - 
**Interpretation**: Of all sessions that landed on a listing page, approximately 76.60% of them resulted in users 
leaving the platform after viewing only the listing page. This is quite high and suggests that many users are not 
proceeding further after checking the general product listings.

2. **Order Page**: - Total Sessions: 7,637 - Bounced Sessions: 943 - Bounce Rate: 12.35% - **Interpretation**: Only 
about 12.35% of sessions that reached the order page ended without further interaction. This is relatively low, 
indicating that most users who reach this page engage further, which is a good sign for conversions.

3. **Product Page**: - Total Sessions: 162,856 - Bounced Sessions: 104,794 - Bounce Rate: 64.35% - 
**Interpretation**: About 64.35% of sessions that landed on a product page ended with users leaving after viewing 
only that product. This suggests potential areas for improvement in terms of product presentation, pricing, reviews, 
or other aspects of the product page.

4. **Search Listing Page**: - Total Sessions: 32,498 - Bounced Sessions: 5,896 - Bounce Rate: 18.14% - 
**Interpretation**: Among sessions that started with a search listing page, 18.14% ended with users leaving after 
their initial search. This indicates that users might be finding relevant products after their search or refining 
their queries for better results.

**Key Insights**:

- The **Listing Page** has the highest bounce rate, suggesting potential challenges in retaining users after they 
view general product listings. - The **Order Page** has the lowest bounce rate, which is a positive indicator for the 
final stages of the user purchase journey. - The **Product Page** and **Search Listing Page** have intermediate 
bounce rates. While the product page might benefit from optimizations, the search listing page's bounce rate suggests 
users are generally finding relevant products after searching.

Understanding these bounce rates can help in optimizing the user journey, enhancing content, and ensuring users find 
what they are looking for, ultimately leading to better conversions."""
st.markdown(markdown_content)

st.subheader(':blue[bounce rate for each page type]')
plot_daily_bounce_rates(data)

## Revisit Rate
st.header('Revisit Rate', divider='rainbow')
st.subheader(':blue[Most loyal users based on the Revisit rate]')
show_loyal_users(data)