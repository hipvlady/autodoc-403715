import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.dates as mdates


def display_visits(data):
    # Total number of users who visited the website
    total_visitors = data['user'].nunique()

    # Users who browsed products (either via Search Listing Page or Listing Page)
    browse_users = data[data['page_type'].isin(['search_listing_page', 'listing_page'])]['user'].nunique()

    # Users who viewed product details
    product_view_users = data[data['page_type'] == 'product_page']['user'].nunique()

    # Users who added products to cart
    add_to_cart_users = data[data['event_type'] == 'add_to_cart']['user'].nunique()

    # Users who made a purchase
    purchased_users = data[data['event_type'] == 'order']['user'].nunique()

    funnel_metrics = {
        'Stage': ['Visit', 'Browse Products', 'View Product Details', 'Add to Cart', 'Purchase'],
        'Number of Users': [total_visitors, browse_users, product_view_users, add_to_cart_users, purchased_users]
    }

    funnel_df = pd.DataFrame(funnel_metrics)
    return funnel_df


def calculate_funnel_user_counts(data):
    # Total number of users who visited the website
    total_visitors = data['user'].nunique()

    # Users who browsed products (either via Search Listing Page or Listing Page)
    browse_users = data[data['page_type'].isin(['search_listing_page', 'listing_page'])]['user'].nunique()

    # Users who viewed product details
    product_view_users = data[data['page_type'] == 'product_page']['user'].nunique()

    # Users who added products to cart
    add_to_cart_users = data[data['event_type'] == 'add_to_cart']['user'].nunique()

    # Users who made a purchase
    purchased_users = data[data['event_type'] == 'order']['user'].nunique()

    # Calculate the conversion rates between each stage of the funnel
    funnel_df = pd.DataFrame({
        'Stage': ['Visit', 'Browse Products', 'View Product Details', 'Add to Cart', 'Purchase'],
        'Number of Users': [total_visitors, browse_users, product_view_users, add_to_cart_users, purchased_users]
    })

    # Calculate conversion rates
    conversion_rates = [(funnel_df['Number of Users'][i] / funnel_df['Number of Users'][i - 1]) * 100
                        if i != 0 else 100 for i in range(len(funnel_df))]

    funnel_df['Conversion Rate (%)'] = conversion_rates
    funnel_df['Conversion Rate (%)'] = funnel_df['Conversion Rate (%)'].apply(lambda x: round(x, 2))

    return funnel_df


def compute_avg_time_by_average_user(data):
    # Ensure event_date is a datetime object
    data['event_date'] = pd.to_datetime(data['event_date'])

    # Extract date from event_date
    data['event_day'] = data['event_date'].dt.date

    # Calculate total duration spent on each page type for each user per day
    total_duration_per_user_day = data.groupby(['user', 'page_type', 'event_day'])['event_date'].apply(
        lambda x: x.max() - x.min()).reset_index(name='duration')

    # Sum durations across all users for each page type per day
    total_duration_per_page_day = total_duration_per_user_day.groupby(['page_type', 'event_day'])['duration'].sum()
    # Count unique users per page type per day
    user_counts_per_page_day = data.groupby(['page_type', 'event_day'])['user'].nunique()
    # Calculate the average duration by dividing total duration by user count
    avg_duration_per_average_user = total_duration_per_page_day / user_counts_per_page_day
    # Convert Timedelta to total seconds and then to minutes
    avg_duration_in_minutes = avg_duration_per_average_user.dt.total_seconds() / 60
    # Create a new DataFrame with the correct column name
    avg_duration_df = avg_duration_in_minutes.reset_index(name='duration')

    return avg_duration_df


def plot_avg_time_by_user(avg_time_by_user):
    # Ensure event_day is a datetime object for plotting
    if not pd.api.types.is_datetime64_any_dtype(avg_time_by_user['event_day']):
        avg_time_by_user['event_day'] = pd.to_datetime(avg_time_by_user['event_day'])

    # Plot
    plt.figure(figsize=(12, 6))
    ax = sns.lineplot(data=avg_time_by_user, x='event_day', y='duration', hue='page_type')
    ax.set_title('Average Time Spent per Page Type by Average User')
    ax.set_ylabel('Average Time (minutes)')
    ax.set_xlabel('Date')
    ax.legend(title='Page Type')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show plot in Streamlit
    st.pyplot(plt)


def plot_heatmap_avg_time_by_user(avg_duration_df):
    # Pivot the data for the heatmap
    heatmap_data = avg_duration_df.pivot(index='event_day', columns='page_type', values='duration')

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".2f")
    plt.title('Average Time Spent on Each Page Type per Day')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust the plot to ensure everything fits without overlapping
    st.pyplot(plt)


def plot_time_spent_by_users(avg_duration_df):
    # Group the data by 'page_type' and calculate the mean duration for each page
    avg_duration_per_page = avg_duration_df.groupby('page_type')['duration'].mean().sort_values(ascending=False)

    # Reset index to convert the Series to a DataFrame for Seaborn
    avg_duration_per_page = avg_duration_per_page.reset_index()

    # Create the bar plot
    plt.figure(figsize=(10, 6))
    bar = sns.barplot(
        x='duration',
        y='page_type',
        data=avg_duration_per_page,
        palette='viridis',
        orient='h'
    )
    plt.xlabel('Average Duration (minutes)')
    plt.ylabel('Page Type')
    plt.title('Average Time Spent by Users on Each Page Type')
    plt.tight_layout()

    # Show values on bars
    for p in bar.patches:
        width = p.get_width()
        plt.text(5+p.get_width(), p.get_y()+0.55*p.get_height(),
                 '{:1.2f}'.format(width),
                 ha='center', va='center')

    # Display the plot in Streamlit
    st.pyplot(plt)


def prepare_data_for_pivot(df):
    # Check if there are any duplicates
    if df.duplicated(subset=['event_day', 'page_type']).any():
        # Resolve duplicates by taking the mean
        df = df.groupby(['event_day', 'page_type']).mean().reset_index()
    return df


def plot_average_duration_with_trendlines(avg_duration_df):
    print(avg_duration_df.head())  # Debug: inspect the DataFrame structure
    print(avg_duration_df.dtypes)  # Debug: check the data types of the columns

    # Ensure 'event_day' is a datetime type for plotting
    avg_duration_df['event_day'] = pd.to_datetime(avg_duration_df['event_day'])

    # Pivot the data to get the correct format for Seaborn
    pivot_df = avg_duration_df.pivot(index="event_day", columns="page_type", values="duration")

    # Prepare the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=pivot_df, ax=ax)

    # Add trendlines
    for page_type in pivot_df.columns:
        sns.regplot(
            x=mdates.date2num(pivot_df.index),
            y=pivot_df[page_type],
            scatter=False,
            order=3,
            label=f"{page_type} Trend",
            ax=ax
        )

    # Set the title and labels
    ax.set_title('Average Duration per Page Type by Date with Trendlines')
    ax.set_ylabel('Average Duration (minutes)')
    ax.set_xlabel('Date')

    # Format the x-ticks to show the date in 'Year-Month-Day' format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Set a locator for each day
    ax.tick_params(axis='x', rotation=45)  # Rotate the x-ticks for better readability

    # Adjust layout
    fig.tight_layout()
    return fig


def plot_common_user_journeys(data):
    # Filter to get sequences of page visits for each session
    user_journey = data.groupby(['user', 'session'])['page_type'].apply(list)

    # Most common journeys
    common_journeys = user_journey.value_counts().head(10)

    # Plotting the most common user journeys
    fig, ax = plt.subplots(figsize=(10, 6))
    common_journeys.plot(kind='barh', ax=ax)
    ax.set_title('Most Common User Journeys')
    ax.set_xlabel('Number of Occurrences')
    ax.invert_yaxis()  # To display the highest count at the top
    plt.tight_layout()  # Adjust the layout so everything fits without overlapping

    return fig


def show_exit_rates(data):
    # Identify the last page viewed in each session
    last_page_per_session = data.groupby('session')['page_type'].last()

    # Count the number of exits for each page
    exit_counts = last_page_per_session.value_counts()

    # Count the total views for each page
    page_views = data['page_type'].value_counts()

    # Calculate the exit rate for each page
    exit_rates = (exit_counts / page_views) * 100

    # Convert the series to a DataFrame for table view
    exit_rate_df = exit_rates.reset_index()
    exit_rate_df.columns = ['Page Type', 'Exit Rate (%)']

    # Display the DataFrame as a table in Streamlit
    st.table(exit_rate_df)


def plot_interactions_before_exit(data):
    # Filter the data for 'add_to_cart' events and get the last interaction before exit per session
    interactions_before_exit = data[data['event_type'] == 'add_to_cart'].groupby('session').last()

    # Count the occurrences of each product in these interactions
    product_counts = interactions_before_exit['product'].value_counts().head(10)

    # Start a figure
    plt.figure(figsize=(10, 6))

    # Use Seaborn to create the bar plot
    sns.barplot(x=product_counts.index, y=product_counts.values)

    # Set the title and labels of the plot
    plt.title('Top 10 Products Added to Cart Before Exiting')
    plt.xlabel('Product')
    plt.ylabel('Count')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Show the plot
    st.pyplot(plt.gcf())


def plot_daily_interactions(data):
    # Resample the data by day and count the interactions
    daily_counts = data.resample('D', on='event_date').size()

    # Start a figure
    plt.figure(figsize=(10, 6))

    # Plot the data
    daily_counts.plot()

    # Set the title and labels of the plot
    plt.title('Daily Interactions Before Exit')
    plt.xlabel('Date')
    plt.ylabel('Number of Interactions')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Ensure everything fits without overlapping
    plt.tight_layout()

    # Show the plot in Streamlit
    st.pyplot(plt.gcf())  # plt.gcf() gets the current figure


def plot_interactions_heatmap(data):
    # Add hour and day of week columns
    data['hour'] = data['event_date'].dt.hour
    data['dayofweek'] = data['event_date'].dt.dayofweek

    # Group by day of week and hour to get counts
    heatmap_data = data.groupby(['dayofweek', 'hour']).size().unstack()

    # Start a figure
    plt.figure(figsize=(12, 8))

    # Create the heatmap
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt="d")

    # Set the title and labels
    plt.title('Interactions Before Exit Heatmap')
    plt.xlabel('Hour of Day')
    plt.ylabel('Day of Week')

    # Optionally, change the labels for days of the week
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    plt.yticks(ticks=np.arange(7), labels=day_labels, rotation=0)  # Set custom labels for the y-axis

    # Ensure everything fits without overlapping
    plt.tight_layout()

    # Show the plot in Streamlit
    st.pyplot(plt.gcf())


def plot_exit_pages_bar_chart(data):
    # Calculate the value counts for the 'page_type' column
    page_type_counts = data['page_type'].value_counts()

    # Start a figure
    plt.figure(figsize=(10, 6))

    # Plot the bar chart
    page_type_counts.plot(kind='bar', color='skyblue')

    # Set the title and labels
    plt.title('Exit Pages Frequency')
    plt.xlabel('Page Type')
    plt.ylabel('Frequency')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Ensure everything fits without overlapping
    plt.tight_layout()

    # Show the plot in Streamlit
    st.pyplot(plt.gcf())


def plot_exit_rate_over_time(data):
    # 1. Identify the exit pages for each session
    exit_pages = data.loc[data.groupby('session')['event_date'].idxmax()]

    # 2. Count exits by day for each page type
    exits_by_day = exit_pages.groupby(['event_day', 'page_type']).size()

    # 3. Count page views by day for each page type
    views_by_day = data.groupby(['event_day', 'page_type']).size()

    # 4. Calculate exit rate by day for each page type
    exit_rate_by_day = (exits_by_day / views_by_day).unstack(level=1) * 100

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 7))
    exit_rate_by_day.plot(ax=ax, title="Exit Rate Over Time", grid=True)
    ax.set_ylabel("Exit Rate (%)")
    ax.set_xlabel("Date")
    ax.legend(title="Page Type")
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)


def show_top_user_paths(data):
    # Extract purchase sessions
    purchase_sessions = data.loc[data['event_type'] == 'order', 'session'].unique()

    # Filter data to only include purchase sessions
    paths_data = data[data['session'].isin(purchase_sessions)]

    # Create the sequence of pages visited in each session
    paths_data['page_sequence'] = paths_data.groupby('session')['page_type'].transform(lambda x: ' -> '.join(x))

    # Get unique paths and their counts
    unique_paths = paths_data[['session', 'page_sequence']].drop_duplicates()
    common_paths = unique_paths.groupby('page_sequence').size().reset_index(name='count').sort_values(by='count',
                                                                                                      ascending=False)

    # Select top 20 paths
    top_20_paths = common_paths.head(20)

    # Display the top 20 paths in Streamlit
    st.write("Top 20 User Paths to Purchase:")
    st.dataframe(top_20_paths)


def show_average_duration_by_page(data):
    # Calculate the start and end time for each session
    session_times = data.groupby('session')['event_date'].agg(['min', 'max'])

    # Calculate the session duration
    session_times['duration'] = ((pd.to_datetime(session_times['max']) - pd.to_datetime(session_times['min'])).
                                 dt.total_seconds())

    # Merge session duration back to the main data to get page_type
    data_with_duration = data.merge(session_times['duration'], left_on='session', right_index=True)

    # Calculate average duration by page type
    average_duration_by_page = data_with_duration.groupby('page_type')['duration'].mean()

    # Convert the Series to a DataFrame
    average_duration_by_page_df = average_duration_by_page.reset_index()

    # Rename columns for better clarity
    average_duration_by_page_df.columns = ['Page Type', 'Average Duration (seconds)']

    # Display the table in Streamlit
    st.table(average_duration_by_page_df)


def calculate_and_display_bounce_rates(data):
    # Calculate the number of events per session
    session_event_counts = data.groupby('session').size()

    # Identify sessions with only one event
    single_event_session_ids = session_event_counts[session_event_counts == 1].index

    # Filter the main data for these sessions
    single_event_sessions = data[data['session'].isin(single_event_session_ids)]

    # Count the bounced sessions per page type
    bounce_sessions_per_page = single_event_sessions.groupby('page_type').session.nunique().reset_index(
        name='bounced_sessions')

    # Merge with total sessions per page type to calculate bounce rate
    total_sessions_per_page = data.groupby('page_type').session.nunique().reset_index(name='total_sessions')
    page_bounce_rates = pd.merge(total_sessions_per_page, bounce_sessions_per_page,
                                 on='page_type', how='left').fillna(0)
    page_bounce_rates['bounce_rate'] = (page_bounce_rates['bounced_sessions'] /
                                        page_bounce_rates['total_sessions']) * 100

    # Display the bounce rates in Streamlit
    st.table(page_bounce_rates)


def plot_daily_bounce_rates(data):
    # Calculate the number of events per session
    session_event_counts = data.groupby('session').size()

    # Identify sessions with only one event
    single_event_session_ids = session_event_counts[session_event_counts == 1].index

    # Filter the main data for these sessions
    single_event_sessions = data[data['session'].isin(single_event_session_ids)]

    # Group by event_day and page_type to count sessions
    daily_page_sessions = data.groupby(['event_day', 'page_type']).session.nunique().reset_index(name='total_sessions')

    # Filter single_event_sessions by event_day and page_type
    daily_single_event_page_sessions = single_event_sessions.groupby(
        ['event_day', 'page_type']).session.nunique().reset_index(name='bounced_sessions')

    # Merge based on event_day and page_type, then calculate bounce rate
    daily_page_bounce_rates = pd.merge(daily_page_sessions, daily_single_event_page_sessions,
                                       on=['event_day', 'page_type'], how='left').fillna(0)
    daily_page_bounce_rates['bounce_rate'] = (daily_page_bounce_rates['bounced_sessions'] /
                                              daily_page_bounce_rates['total_sessions']) * 100

    # Plot bounce rate for each page type
    fig, ax = plt.subplots(figsize=(15, 8))
    for page_type in daily_page_bounce_rates['page_type'].unique():
        subset = daily_page_bounce_rates[daily_page_bounce_rates['page_type'] == page_type]
        ax.plot(subset['event_day'], subset['bounce_rate'], label=page_type, marker='o')

    ax.set_xlabel('Date')
    ax.set_ylabel('Bounce Rate (%)')
    ax.set_title('Daily Bounce Rate Over Time by Page Type')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))  # Limit the number of x-ticks to make the plot readable
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)


def show_loyal_users(data, top_n=20):
    # Calculate the number of sessions per user
    user_visits = data.groupby('user').session.nunique().sort_values(ascending=False)

    # Top N users with the most visits
    loyal_users_ranked = user_visits.head(top_n)

    st.subheader(f'Top {top_n} Loyal Users')
    st.write(loyal_users_ranked)
