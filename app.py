import streamlit as st

import preprocessor
import utility
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    try:
        user_list.remove('group_notifications')
    except:
        pass
    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_option = st.sidebar.selectbox("Show Analysis", user_list)

    if st.sidebar.button("Show Analysis"):
        # stats area
        num_messages, words, num_media, num_links = utility.fetch_stats(selected_option, df)

        st.title('Top Statistics')
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
        with col4:
            st.header("Links Shared")
            st.title(num_links)
        # monthly timeline
        st.title("Monthly Timeline")
        timeline = utility.monthly_timeline(selected_option, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['messages'], color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        timeline = utility.daily_timeline(selected_option, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['modified_date'], timeline['messages'], color='magenta')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # week activity
        st.title("Weekly Activity")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy day")
            busy_day = utility.week_activity(selected_option, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = utility.month_activity(selected_option, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # heatmap
        st.title("Weekly Activity Map")
        user_heatmap = utility.activity_heatmap(selected_option, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap, cmap='YlGnBu')
        st.pyplot(fig)

        # most active user
        if selected_option == 'Overall':
            st.title('Most Active Users')
            x, percent_df = utility.most_active_user(df)
            name = x.index
            count = x.values
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(name, count, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(percent_df)
        # WordCloud
        st.title('WordCloud')
        df_wc = utility.create_wordcloud(selected_option, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_words_df, emoji_df, profane_df = utility.most_common_words_emojis_and_profane_words(selected_option,
                                                                                                        df)
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        fig, ax = plt.subplots()
        ax.barh(most_common_words_df[0], most_common_words_df[1], color='purple')
        plt.xticks(rotation='vertical')
        st.title('Most Common Words Used')
        st.pyplot(fig)

        # emoji analysis
        st.title("Emoji Analysis")
        if emoji_df is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)
        else:
            st.text("No emojis used")

        # profanity analysis
        st.title("Profanity Analysis")
        if profane_df is not None:
            fig, ax = plt.subplots()
            ax.barh(profane_df[0], profane_df[1], color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.text("Clean Messages")

        # threat analysis
        st.header("Most Sensitive Messages are")
        sensitive_df = utility.sensitive_messages(selected_option, df)
        if sensitive_df is None:
            st.text("No Sensitive Messages")
        else:
            st.dataframe(sensitive_df, use_container_width=True)

