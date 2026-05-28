import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


DEFAULT_DATA_PATH = Path(
    r"C:\Users\dtw12\OneDrive\Documents\Projects\Data Analytics Projects\Netflix Data Analysis\netflix_titles.csv"
)


st.set_page_config(
    page_title="Netflix Content Dashboard",
    page_icon="N",
    layout="wide",
)


@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="latin1")

    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month
    df["month_name_added"] = df["date_added"].dt.month_name()

    df["duration_number"] = df["duration"].str.extract(r"(\d+)").astype(float)
    df["runtime_minutes"] = df["duration_number"].where(df["type"].eq("Movie"))
    df["seasons"] = df["duration_number"].where(df["type"].eq("TV Show"))

    return df


def make_genre_counts(data: pd.DataFrame) -> pd.Series:
    genres = data["listed_in"].dropna().str.get_dummies(sep=", ")
    return genres.sum().sort_values(ascending=False)


def split_multi_value_counts(data: pd.DataFrame, column: str) -> pd.Series:
    return (
        data[column]
        .dropna()
        .str.split(", ")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )


def show_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, horizontal: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    if horizontal:
        series.sort_values().plot(kind="barh", ax=ax)
    else:
        series.plot(kind="bar", ax=ax)
        ax.tick_params(axis="x", rotation=45)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    st.pyplot(fig, clear_figure=True)


def sidebar_filters(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    content_types = sorted(data["type"].dropna().unique())
    selected_types = st.sidebar.multiselect(
        "Content type",
        content_types,
        default=content_types,
    )

    ratings = sorted(data["rating"].dropna().unique())
    selected_ratings = st.sidebar.multiselect(
        "Rating",
        ratings,
        default=ratings,
    )

    min_year = int(data["release_year"].min())
    max_year = int(data["release_year"].max())
    release_range = st.sidebar.slider(
        "Release year",
        min_year,
        max_year,
        (min_year, max_year),
    )

    filtered = data[
        data["type"].isin(selected_types)
        & data["rating"].isin(selected_ratings)
        & data["release_year"].between(release_range[0], release_range[1])
    ]

    return filtered


csv_path = os.environ.get("NETFLIX_DATA_PATH", str(DEFAULT_DATA_PATH))

st.title("Netflix Content Dashboard")
st.caption("Interactive dashboard built from the Netflix Data Analysis Python file.")

with st.sidebar:
    st.write("Data source")
    csv_path = st.text_input("CSV path", csv_path)

try:
    df = load_data(csv_path)
except FileNotFoundError:
    st.error("CSV file not found. Update the CSV path in the sidebar.")
    st.stop()
except Exception as exc:
    st.error(f"Could not load the CSV file: {exc}")
    st.stop()

filtered_df = sidebar_filters(df)

total_titles = len(filtered_df)
movie_count = int((filtered_df["type"] == "Movie").sum())
tv_count = int((filtered_df["type"] == "TV Show").sum())
country_count = split_multi_value_counts(filtered_df, "country").shape[0]

metric_cols = st.columns(4)
metric_cols[0].metric("Total titles", f"{total_titles:,}")
metric_cols[1].metric("Movies", f"{movie_count:,}")
metric_cols[2].metric("TV shows", f"{tv_count:,}")
metric_cols[3].metric("Countries", f"{country_count:,}")

tab_overview, tab_genres, tab_duration, tab_catalog = st.tabs(
    ["Overview", "Genres & countries", "Duration", "Catalog"]
)

with tab_overview:
    left_col, right_col = st.columns(2)

    type_counts = filtered_df["type"].value_counts()
    fig_type, ax_type = plt.subplots(figsize=(6, 5))
    ax_type.pie(
        type_counts,
        labels=type_counts.index,
        autopct="%1.1f%%",
        startangle=140,
    )
    ax_type.set_title("Movies vs TV shows")
    left_col.pyplot(fig_type, clear_figure=True)

    with right_col:
        show_bar_chart(
            filtered_df["rating"].value_counts(),
            "Viewer rating distribution",
            "Rating",
            "Titles",
        )

    yearly_counts = (
        filtered_df.dropna(subset=["year_added"])
        .groupby("year_added")
        .size()
        .sort_index()
    )
    fig_year, ax_year = plt.subplots(figsize=(11, 5))
    yearly_counts.plot(kind="line", marker="o", ax=ax_year)
    ax_year.set_title("Content added over the years")
    ax_year.set_xlabel("Year added")
    ax_year.set_ylabel("Titles added")
    st.pyplot(fig_year, clear_figure=True)

with tab_genres:
    left_col, right_col = st.columns(2)

    with left_col:
        show_bar_chart(
            make_genre_counts(filtered_df).head(15),
            "Top 15 genres on Netflix",
            "Titles",
            "Genre",
            horizontal=True,
        )

    with right_col:
        show_bar_chart(
            split_multi_value_counts(filtered_df, "country").head(10),
            "Top 10 production countries",
            "Country",
            "Titles",
        )

with tab_duration:
    movie_df = filtered_df[filtered_df["type"] == "Movie"].dropna(subset=["runtime_minutes"])
    tv_df = filtered_df[filtered_df["type"] == "TV Show"].dropna(subset=["seasons"])

    left_col, right_col = st.columns(2)

    fig_runtime, ax_runtime = plt.subplots(figsize=(8, 5))
    ax_runtime.hist(movie_df["runtime_minutes"], bins=30, edgecolor="black")
    ax_runtime.set_title("Distribution of movie runtimes")
    ax_runtime.set_xlabel("Runtime in minutes")
    ax_runtime.set_ylabel("Movies")
    left_col.pyplot(fig_runtime, clear_figure=True)

    season_counts = tv_df["seasons"].value_counts().sort_index().reset_index()
    season_counts.columns = ["seasons", "count"]
    fig_seasons, ax_seasons = plt.subplots(figsize=(8, 5))
    ax_seasons.bar(season_counts["seasons"], season_counts["count"])
    ax_seasons.set_title("Distribution of TV show seasons")
    ax_seasons.set_xlabel("Number of seasons")
    ax_seasons.set_ylabel("TV shows")
    right_col.pyplot(fig_seasons, clear_figure=True)

with tab_catalog:
    search = st.text_input("Search by title")
    catalog_df = filtered_df.copy()
    if search:
        catalog_df = catalog_df[
            catalog_df["title"].str.contains(search, case=False, na=False)
        ]

    display_columns = [
        "title",
        "type",
        "release_year",
        "rating",
        "duration",
        "country",
        "listed_in",
        "date_added",
    ]
    st.dataframe(
        catalog_df[display_columns].sort_values(["release_year", "title"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )
