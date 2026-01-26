import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from typing import Dict, List

# Set up teal color palette for charts
TEAL_PALETTE = ["#0D9488", "#14B8A6", "#2DD4BF", "#5EEAD4", "#99F6E4", "#CCFBF1"]
TEAL_CMAP = sns.light_palette("#0D9488", as_cmap=True)

# Configure matplotlib/seaborn defaults
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.edgecolor'] = '#E2E8F0'
plt.rcParams['axes.labelcolor'] = '#64748B'
plt.rcParams['xtick.color'] = '#64748B'
plt.rcParams['ytick.color'] = '#64748B'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
sns.set_palette(TEAL_PALETTE)


def detect_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Automatically detect column types in the DataFrame.
    
    Returns:
        Dict with keys: 'numeric', 'categorical', 'datetime', 'text'
    """
    column_types = {
        'numeric': [],
        'categorical': [],
        'datetime': [],
        'text': []
    }
    
    for col in df.columns:
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types['datetime'].append(col)
        # Check for numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            column_types['numeric'].append(col)
        # Check for text (long strings, high cardinality)
        elif df[col].dtype == 'object':
            # If average string length > 50 or unique ratio > 0.5, consider it text
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            avg_length = df[col].astype(str).str.len().mean()
            
            if avg_length > 50 or unique_ratio > 0.5:
                column_types['text'].append(col)
            else:
                column_types['categorical'].append(col)
        else:
            column_types['categorical'].append(col)
    
    return column_types


def display_column_types(df: pd.DataFrame):
    """Display detected column types in a nice format."""
    col_types = detect_column_types(df)
    
    st.subheader("Column Type Detection")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Numeric", len(col_types['numeric']))
        if col_types['numeric']:
            with st.expander("View numeric columns"):
                for col in col_types['numeric']:
                    st.write(f"• {col}")
    
    with col2:
        st.metric("Categorical", len(col_types['categorical']))
        if col_types['categorical']:
            with st.expander("View categorical columns"):
                for col in col_types['categorical']:
                    st.write(f"• {col}")
    
    with col3:
        st.metric("Datetime", len(col_types['datetime']))
        if col_types['datetime']:
            with st.expander("View datetime columns"):
                for col in col_types['datetime']:
                    st.write(f"• {col}")
    
    with col4:
        st.metric("Text", len(col_types['text']))
        if col_types['text']:
            with st.expander("View text columns"):
                for col in col_types['text']:
                    st.write(f"• {col}")
    
    return col_types


def analyze_csv(df: pd.DataFrame, key_prefix="default", initial_config=None):
    # display stats, missing values and charts
    st.subheader("Summary Statistics")
    st.dataframe(df.describe(include="all").T)

    st.subheader("Missing Values")
    missing = df.isnull().sum().reset_index()
    missing.columns = ['Column', 'Missing Count']
    st.dataframe(missing)

    st.subheader("Correlation Heatmap")
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(numeric.corr(), annot=True, cmap=TEAL_CMAP, ax=ax,
                    linewidths=0.5, linecolor='white',
                    cbar_kws={'shrink': 0.8})
        ax.set_title("Feature Correlations", fontsize=14, fontweight='600', color='#0F172A', pad=15)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No numeric columns found for correlation.")

    st.subheader("Quick Plot")

    plot_col_key = f"{key_prefix}_plot_column"
    plot_type_key = f"{key_prefix}_plot_type"

    if initial_config:
        qp = initial_config.get("quick_plot", {})
        col_default = qp.get("column")
        type_default = qp.get("chart_type")
        if col_default in df.columns and plot_col_key not in st.session_state:
            st.session_state[plot_col_key] = col_default
        if type_default in ["Bar", "Pie", "Histogram", "Line"] and plot_type_key not in st.session_state:
            st.session_state[plot_type_key] = type_default

    col = st.selectbox(
        "Select column to plot:",
        df.columns,
        key=plot_col_key
    )
    chart_type = st.selectbox(
        "Choose chart type:",
        ["Bar", "Pie", "Histogram", "Line"],
        key=plot_type_key
    )

    fig, ax = plt.subplots()

    if chart_type == "Bar":
        counts = df[col].astype(str).value_counts()
        if counts.empty or counts.nunique() == len(df):
            st.warning("Nothing meaningful to plot as a bar chart.")
        else:
            counts.head(20).plot(kind="bar", ax=ax, color='#0D9488', edgecolor='white')
            ax.set_ylabel("Count", fontsize=10, color='#64748B')
            ax.set_title(f"Distribution of {col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            plt.xticks(rotation=45, ha="right", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)

    elif chart_type == "Pie":
        counts = df[col].astype(str).value_counts()
        if counts.empty or counts.nunique() > 10:
            st.warning("Pie chart works best for a small number of categories.")
        else:
            counts.plot(kind="pie", autopct="%1.1f%%", ax=ax, colors=TEAL_PALETTE,
                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            ax.set_ylabel("")
            ax.set_title(f"Distribution of {col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            plt.tight_layout()
            st.pyplot(fig)

    elif chart_type == "Histogram":
        if pd.api.types.is_numeric_dtype(df[col]):
            sns.histplot(df[col], kde=True, ax=ax, color='#0D9488', edgecolor='white',
                        line_kws={'color': '#0F766E', 'linewidth': 2})
            ax.set_title(f"Distribution of {col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            ax.set_xlabel(col, fontsize=10, color='#64748B')
            ax.set_ylabel("Frequency", fontsize=10, color='#64748B')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Histogram only works for numeric columns.")

    elif chart_type == "Line":
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col].reset_index(drop=True).plot(kind="line", ax=ax, color='#0D9488', linewidth=2)
            ax.set_ylabel(col, fontsize=10, color='#64748B')
            ax.set_xlabel("Index", fontsize=10, color='#64748B')
            ax.set_title(f"Trend of {col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            ax.fill_between(range(len(df[col])), df[col].values, alpha=0.1, color='#0D9488')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Line chart only works for numeric columns.")

    st.subheader("Compare Two Columns")

    cmp_x_key = f"{key_prefix}_cmp_x"
    cmp_y_key = f"{key_prefix}_cmp_y"
    cmp_type_key = f"{key_prefix}_cmp_type"

    if initial_config:
        cmp_cfg = initial_config.get("compare", {})
        x_default = cmp_cfg.get("x")
        y_default = cmp_cfg.get("y")
        t_default = cmp_cfg.get("comparison_type")
        if x_default in df.columns and cmp_x_key not in st.session_state:
            st.session_state[cmp_x_key] = x_default
        if y_default in df.columns and cmp_y_key not in st.session_state:
            st.session_state[cmp_y_key] = y_default
        if t_default in ["Scatter", "Line", "Bar", "Correlation"] and cmp_type_key not in st.session_state:
            st.session_state[cmp_type_key] = t_default

    c1, c2 = st.columns(2)
    x_col = c1.selectbox(
        "Select X-axis",
        df.columns,
        key=cmp_x_key
    )
    y_col = c2.selectbox(
        "Select Y-axis",
        df.columns,
        key=cmp_y_key
    )

    compare_type = st.selectbox(
        "Comparison type:",
        ["Scatter", "Line", "Bar", "Correlation"],
        key=cmp_type_key
    )

    fig, ax = plt.subplots()

    if compare_type == "Scatter":
        if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
            sns.scatterplot(x=df[x_col], y=df[y_col], ax=ax, color='#0D9488', alpha=0.7, edgecolor='white')
            ax.set_xlabel(x_col, fontsize=10, color='#64748B')
            ax.set_ylabel(y_col, fontsize=10, color='#64748B')
            ax.set_title(f"{x_col} vs {y_col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Scatter comparison works only for numeric columns.")

    elif compare_type == "Line":
        if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
            df.plot(x=x_col, y=y_col, kind="line", ax=ax, color='#0D9488', linewidth=2)
            ax.set_title(f"{y_col} over {x_col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            ax.set_xlabel(x_col, fontsize=10, color='#64748B')
            ax.set_ylabel(y_col, fontsize=10, color='#64748B')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Line comparison works best with numeric columns.")

    elif compare_type == "Bar":
        grouped = (
            df.groupby(x_col)[y_col]
            .mean(numeric_only=True)
            .sort_values(ascending=False)
            .head(10)
        )
        if grouped.empty:
            st.warning("Bar comparison requires numeric Y and categorical X.")
        else:
            grouped.plot(kind="bar", ax=ax, color='#0D9488', edgecolor='white')
            ax.set_xlabel(x_col, fontsize=10, color='#64748B')
            ax.set_ylabel(f"Average {y_col}", fontsize=10, color='#64748B')
            ax.set_title(f"{y_col} by {x_col}", fontsize=12, fontweight='600', color='#0F172A', pad=10)
            plt.xticks(rotation=45, ha="right", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)

    elif compare_type == "Correlation":
        numeric_pair = df[[x_col, y_col]].select_dtypes(include="number")
        if numeric_pair.shape[1] == 2:
            corr = numeric_pair.corr().iloc[0, 1]
            st.metric(
                label=f"Correlation between {x_col} and {y_col}",
                value=round(float(corr), 3)
            )
        else:
            st.warning("Correlation comparison works only for numeric columns.")

    config = {
        "quick_plot": {
            "column": st.session_state.get(plot_col_key, col),
            "chart_type": st.session_state.get(plot_type_key, chart_type)
        },
        "compare": {
            "x": st.session_state.get(cmp_x_key, x_col),
            "y": st.session_state.get(cmp_y_key, y_col),
            "comparison_type": st.session_state.get(cmp_type_key, compare_type)
        }
    }
    return config
