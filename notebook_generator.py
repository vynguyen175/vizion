import nbformat as nbf
import pandas as pd
from typing import Dict, List, Optional
import os


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
            unique_ratio = df[col].nunique() / len(df)
            avg_length = df[col].astype(str).str.len().mean()
            
            if avg_length > 50 or unique_ratio > 0.5:
                column_types['text'].append(col)
            else:
                column_types['categorical'].append(col)
        else:
            column_types['categorical'].append(col)
    
    return column_types


def suggest_ml_task(df: pd.DataFrame, target_column: Optional[str]) -> Dict[str, str]:
    """
    Suggest ML task type based on target column.
    
    Returns:
        Dict with 'task_type' and 'reason'
    """
    if not target_column or target_column not in df.columns:
        return {
            'task_type': 'eda',
            'reason': 'No target column specified. Will perform exploratory data analysis only.'
        }
    
    target_data = df[target_column]
    
    # Check if numeric
    if pd.api.types.is_numeric_dtype(target_data):
        unique_count = target_data.nunique()
        
        # Binary classification
        if unique_count == 2:
            return {
                'task_type': 'binary_classification',
                'reason': f'Target "{target_column}" has 2 unique values (binary classification).'
            }
        # Multi-class classification (reasonable number of classes)
        elif unique_count <= 20:
            return {
                'task_type': 'multiclass_classification',
                'reason': f'Target "{target_column}" has {unique_count} unique classes.'
            }
        # Regression
        else:
            return {
                'task_type': 'regression',
                'reason': f'Target "{target_column}" is continuous numeric with {unique_count} unique values.'
            }
    else:
        # Categorical target
        unique_count = target_data.nunique()
        
        if unique_count == 2:
            return {
                'task_type': 'binary_classification',
                'reason': f'Target "{target_column}" is categorical with 2 classes.'
            }
        elif unique_count <= 20:
            return {
                'task_type': 'multiclass_classification',
                'reason': f'Target "{target_column}" is categorical with {unique_count} classes.'
            }
        else:
            return {
                'task_type': 'regression',
                'reason': f'Target "{target_column}" has too many categories ({unique_count}), treating as regression.'
            }


def generate_ml_notebook(
    csv_path: str,
    output_path: str,
    target_column: Optional[str] = None,
    model_type: Optional[str] = None,
    task_type: str = 'eda'
) -> str:
    """
    Generate a Jupyter notebook for ML analysis.
    
    Args:
        csv_path: Path to the CSV file
        output_path: Where to save the notebook
        target_column: Target variable for prediction (None for EDA only)
        model_type: Specific model to use (e.g., 'logistic_regression', 'random_forest')
        task_type: Type of ML task ('eda', 'binary_classification', 'multiclass_classification', 'regression')
    
    Returns:
        Path to the generated notebook
    """
    nb = nbf.v4.new_notebook()
    cells = []
    
    # Cell 1: Title
    cells.append(nbf.v4.new_markdown_cell(f"""# Machine Learning Analysis Report
    
**Dataset:** {os.path.basename(csv_path)}  
**Task Type:** {task_type.replace('_', ' ').title()}  
**Target Column:** {target_column if target_column else 'N/A (EDA Only)'}  
**Generated:** Automated by Vizion  
"""))
    
    # Cell 2: Import dependencies
    import_code = """# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
"""
    
    if task_type != 'eda':
        import_code += """
# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
"""
        
        if task_type in ['binary_classification', 'multiclass_classification']:
            import_code += """
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
"""
        else:
            import_code += """
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
"""
    
    cells.append(nbf.v4.new_code_cell(import_code))
    
    # Cell 3: Load data
    cells.append(nbf.v4.new_markdown_cell("## 1. Load Dataset"))
    cells.append(nbf.v4.new_code_cell(f"""# Load the dataset
df = pd.read_csv(r"{csv_path}")

print(f"Dataset shape: {{df.shape[0]}} rows, {{df.shape[1]}} columns")
df.head()
"""))
    
    # Cell 4: Data Overview
    cells.append(nbf.v4.new_markdown_cell("## 2. Data Overview"))
    cells.append(nbf.v4.new_code_cell("""# Basic information
print("Dataset Info:")
print(df.info())
print("\\n" + "="*50 + "\\n")

print("Statistical Summary:")
print(df.describe())
print("\\n" + "="*50 + "\\n")

print("Missing Values:")
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Percentage': missing_pct
})
print(missing_df[missing_df['Missing Count'] > 0])
"""))
    
    # Cell 5: Column Types Detection
    cells.append(nbf.v4.new_markdown_cell("## 3. Column Type Detection"))
    cells.append(nbf.v4.new_code_cell("""# Detect column types
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"Numeric columns ({len(numeric_cols)}): {numeric_cols}")
print(f"Categorical columns ({len(categorical_cols)}): {categorical_cols}")
"""))
    
    # Cell 6: Exploratory Data Analysis
    cells.append(nbf.v4.new_markdown_cell("## 4. Exploratory Data Analysis"))
    
    # Correlation heatmap
    cells.append(nbf.v4.new_code_cell("""# Correlation heatmap for numeric features
if len(numeric_cols) > 1:
    plt.figure(figsize=(12, 8))
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()
else:
    print("Not enough numeric columns for correlation analysis")
"""))
    
    # Distribution plots
    cells.append(nbf.v4.new_code_cell("""# Distribution of numeric features
if len(numeric_cols) > 0:
    n_cols = min(4, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes]
    
    for idx, col in enumerate(numeric_cols[:len(axes)]):
        df[col].hist(bins=30, ax=axes[idx], edgecolor='black')
        axes[idx].set_title(f'Distribution of {col}')
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel('Frequency')
    
    # Hide extra subplots
    for idx in range(len(numeric_cols), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.show()
"""))
    
    # Categorical distributions
    cells.append(nbf.v4.new_code_cell("""# Categorical feature analysis
if len(categorical_cols) > 0:
    for col in categorical_cols[:5]:  # Show first 5 categorical columns
        print(f"\\nValue counts for '{col}':")
        value_counts = df[col].value_counts().head(10)
        print(value_counts)
        
        if len(value_counts) <= 10:
            plt.figure(figsize=(10, 4))
            value_counts.plot(kind='bar')
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
"""))
    
    # If ML task, add preprocessing and modeling
    if task_type != 'eda' and target_column:
        # Cell: Preprocessing
        cells.append(nbf.v4.new_markdown_cell("## 5. Data Preprocessing"))
        
        preprocessing_code = f"""# Prepare data for modeling
# Separate features and target
X = df.drop('{target_column}', axis=1)
y = df['{target_column}']

print(f"Features shape: {{X.shape}}")
print(f"Target shape: {{y.shape}}")
print(f"\\nTarget distribution:")
print(y.value_counts())
"""
        
        if task_type in ['binary_classification', 'multiclass_classification']:
            preprocessing_code += """
# Encode target if categorical
if y.dtype == 'object':
    le = LabelEncoder()
    y = le.fit_transform(y)
    print(f"\\nTarget encoded. Classes: {le.classes_}")
"""
        
        preprocessing_code += """
# Handle missing values
if X.isnull().sum().sum() > 0:
    print("\\nHandling missing values...")
    # Fill numeric columns with median
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_features:
        X[col].fillna(X[col].median(), inplace=True)
    
    # Fill categorical columns with mode
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    for col in categorical_features:
        X[col].fillna(X[col].mode()[0], inplace=True)

# Encode categorical features
categorical_features = X.select_dtypes(include=['object', 'category']).columns
if len(categorical_features) > 0:
    print(f"\\nEncoding categorical features: {list(categorical_features)}")
    X = pd.get_dummies(X, columns=categorical_features, drop_first=True)

print(f"\\nFinal feature shape after encoding: {X.shape}")
print(f"Features: {X.columns.tolist()[:10]}..." if len(X.columns) > 10 else f"Features: {X.columns.tolist()}")
"""
        
        cells.append(nbf.v4.new_code_cell(preprocessing_code))
        
        # Cell: Train-Test Split
        cells.append(nbf.v4.new_markdown_cell("## 6. Train-Test Split"))
        cells.append(nbf.v4.new_code_cell("""# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) < 50 else None
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set: {X_test.shape[0]} samples")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\\nFeatures scaled using StandardScaler")
"""))
        
        # Cell: Model Training
        cells.append(nbf.v4.new_markdown_cell("## 7. Model Training"))
        
        # Determine which models to use
        if model_type:
            model_code = get_specific_model_code(model_type, task_type)
        else:
            model_code = get_default_models_code(task_type)
        
        cells.append(nbf.v4.new_code_cell(model_code))
        
        # Cell: Model Evaluation
        cells.append(nbf.v4.new_markdown_cell("## 8. Model Evaluation"))
        
        if task_type in ['binary_classification', 'multiclass_classification']:
            eval_code = """# Evaluate the model
y_pred = best_model.predict(X_test_scaled)

print("Model Performance:")
print("="*50)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Recall: {recall_score(y_test, y_pred, average='weighted'):.4f}")
print(f"F1-Score: {f1_score(y_test, y_pred, average='weighted'):.4f}")

print("\\n" + "="*50)
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()
"""
        else:  # Regression
            eval_code = """# Evaluate the model
y_pred = best_model.predict(X_test_scaled)

print("Model Performance:")
print("="*50)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred):.4f}")
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.4f}")
print(f"Root Mean Squared Error: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")

# Residual Plot
plt.figure(figsize=(10, 6))
residuals = y_test - y_pred
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residual Plot')
plt.show()

# Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Actual vs Predicted')
plt.show()
"""
        
        cells.append(nbf.v4.new_code_cell(eval_code))
        
        # Cell: Feature Importance
        cells.append(nbf.v4.new_markdown_cell("## 9. Feature Importance"))
        cells.append(nbf.v4.new_code_cell("""# Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("Top 10 Most Important Features:")
    print(feature_importance.head(10))
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    top_features = feature_importance.head(15)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title('Top 15 Feature Importances')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
elif hasattr(best_model, 'coef_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'coefficient': best_model.coef_[0] if len(best_model.coef_.shape) > 1 else best_model.coef_
    }).sort_values('coefficient', ascending=False, key=abs)
    
    print("Top 10 Most Important Features (by coefficient magnitude):")
    print(feature_importance.head(10))
    
    # Plot coefficients
    plt.figure(figsize=(10, 6))
    top_features = feature_importance.head(15)
    plt.barh(range(len(top_features)), top_features['coefficient'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Coefficient Value')
    plt.title('Top 15 Feature Coefficients')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
else:
    print("Feature importance not available for this model")
"""))
    
    # Final summary cell
    cells.append(nbf.v4.new_markdown_cell("""## 10. Conclusion

### Key Findings:
- Dataset successfully analyzed and preprocessed
- Model trained and evaluated on test data
- Feature importance extracted to understand key predictors

### Recommendations:
- Review feature importance to understand which variables drive predictions
- Consider collecting more data if model performance is suboptimal
- Try different models or hyperparameter tuning for improved results
- Monitor model performance on new data

---
*This notebook was automatically generated by Vizion ML Engine*
"""))
    
    # Assign cells to notebook
    nb['cells'] = cells
    
    # Write notebook to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    return output_path


def get_default_models_code(task_type: str) -> str:
    """Generate code for training multiple models and selecting the best."""
    
    if task_type in ['binary_classification', 'multiclass_classification']:
        return """# Train multiple classification models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)
}

results = {}
print("Training and evaluating models...")
print("="*50)

for name, model in models.items():
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    print(f"\\n{name}:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")

# Select best model based on accuracy
best_model_name = max(results, key=lambda x: results[x]['accuracy'])
best_model = results[best_model_name]['model']

print("\\n" + "="*50)
print(f"\\nBest Model: {best_model_name}")
print(f"Best Accuracy: {results[best_model_name]['accuracy']:.4f}")
"""
    else:  # Regression
        return """# Train multiple regression models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
}

results = {}
print("Training and evaluating models...")
print("="*50)

for name, model in models.items():
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    
    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    results[name] = {
        'model': model,
        'r2': r2,
        'mae': mae,
        'mse': mse,
        'rmse': rmse
    }
    
    print(f"\\n{name}:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")

# Select best model based on R² score
best_model_name = max(results, key=lambda x: results[x]['r2'])
best_model = results[best_model_name]['model']

print("\\n" + "="*50)
print(f"\\nBest Model: {best_model_name}")
print(f"Best R² Score: {results[best_model_name]['r2']:.4f}")
"""


def get_specific_model_code(model_type: str, task_type: str) -> str:
    """Generate code for a specific model."""
    
    model_map = {
        'logistic_regression': ('LogisticRegression', 'LogisticRegression(max_iter=1000, random_state=42)'),
        'random_forest': ('Random Forest', 'RandomForestClassifier(n_estimators=100, random_state=42)' if 'classification' in task_type else 'RandomForestRegressor(n_estimators=100, random_state=42)'),
        'gradient_boosting': ('Gradient Boosting', 'GradientBoostingClassifier(n_estimators=100, random_state=42)' if 'classification' in task_type else 'GradientBoostingRegressor(n_estimators=100, random_state=42)'),
        'knn': ('K-Nearest Neighbors', 'KNeighborsClassifier(n_neighbors=5)'),
        'linear_regression': ('Linear Regression', 'LinearRegression()'),
        'ridge': ('Ridge Regression', 'Ridge(alpha=1.0, random_state=42)')
    }
    
    model_name, model_init = model_map.get(model_type, ('Random Forest', 'RandomForestClassifier(n_estimators=100, random_state=42)'))
    
    return f"""# Train {model_name} model
print("Training {model_name}...")
best_model = {model_init}
best_model.fit(X_train_scaled, y_train)

print(f"Model trained successfully!")
print(f"Model: {{best_model}}")
"""
