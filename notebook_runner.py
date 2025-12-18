import papermill as pm
import nbformat
import json
import os
from typing import Dict, Optional, List
import re


def execute_notebook(
    notebook_path: str,
    output_notebook_path: str,
    parameters: Optional[Dict] = None
) -> Dict:
    """
    Execute a Jupyter notebook using Papermill.
    
    Args:
        notebook_path: Path to the notebook to execute
        output_notebook_path: Where to save the executed notebook
        parameters: Dictionary of parameters to inject into the notebook
    
    Returns:
        Dict with execution results including success status, errors, and extracted metrics
    """
    result = {
        'success': False,
        'error': None,
        'metrics': {},
        'output_path': output_notebook_path
    }
    
    try:
        # Execute notebook with papermill
        pm.execute_notebook(
            notebook_path,
            output_notebook_path,
            parameters=parameters or {},
            kernel_name='python3'
        )
        
        result['success'] = True
        
        # Extract results from executed notebook
        result['metrics'] = extract_metrics_from_notebook(output_notebook_path)
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
    
    return result


def extract_metrics_from_notebook(notebook_path: str) -> Dict:
    """
    Extract ML metrics and results from an executed notebook.
    
    Returns:
        Dict containing extracted metrics like accuracy, precision, feature importance, etc.
    """
    metrics = {
        'model_name': None,
        'accuracy': None,
        'precision': None,
        'recall': None,
        'f1_score': None,
        'r2_score': None,
        'mae': None,
        'rmse': None,
        'feature_importance': [],
        'confusion_matrix': None,
        'training_samples': None,
        'testing_samples': None
    }
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Iterate through cells and extract metrics from outputs
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'outputs' in cell:
                for output in cell.outputs:
                    if output.output_type == 'stream' and 'text' in output:
                        text = output.text
                        
                        # Extract model name
                        model_match = re.search(r'Best Model:\s*(.+)', text)
                        if model_match:
                            metrics['model_name'] = model_match.group(1).strip()
                        
                        # Extract classification metrics
                        accuracy_match = re.search(r'Accuracy:\s*([\d.]+)', text)
                        if accuracy_match:
                            metrics['accuracy'] = float(accuracy_match.group(1))
                        
                        precision_match = re.search(r'Precision:\s*([\d.]+)', text)
                        if precision_match:
                            metrics['precision'] = float(precision_match.group(1))
                        
                        recall_match = re.search(r'Recall:\s*([\d.]+)', text)
                        if recall_match:
                            metrics['recall'] = float(recall_match.group(1))
                        
                        f1_match = re.search(r'F1-Score:\s*([\d.]+)', text)
                        if f1_match:
                            metrics['f1_score'] = float(f1_match.group(1))
                        
                        # Extract regression metrics
                        r2_match = re.search(r'R² Score:\s*([\d.]+)', text)
                        if r2_match:
                            metrics['r2_score'] = float(r2_match.group(1))
                        
                        mae_match = re.search(r'Mean Absolute Error:\s*([\d.]+)', text)
                        if mae_match:
                            metrics['mae'] = float(mae_match.group(1))
                        
                        rmse_match = re.search(r'Root Mean Squared Error:\s*([\d.]+)', text)
                        if rmse_match:
                            metrics['rmse'] = float(rmse_match.group(1))
                        
                        # Extract training/testing split info
                        train_match = re.search(r'Training set:\s*(\d+)\s*samples', text)
                        if train_match:
                            metrics['training_samples'] = int(train_match.group(1))
                        
                        test_match = re.search(r'Testing set:\s*(\d+)\s*samples', text)
                        if test_match:
                            metrics['testing_samples'] = int(test_match.group(1))
    
    except Exception as e:
        print(f"Warning: Could not extract metrics from notebook: {e}")
    
    return metrics


def convert_notebook_to_html(notebook_path: str, output_html_path: str) -> bool:
    """
    Convert a Jupyter notebook to HTML format.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import subprocess
        
        result = subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'html', notebook_path, '--output', output_html_path],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"Error converting notebook to HTML: {e}")
        return False


def convert_notebook_to_python(notebook_path: str, output_py_path: str) -> bool:
    """
    Convert a Jupyter notebook to a Python script.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        python_code = []
        python_code.append("# Generated from Jupyter Notebook")
        python_code.append("# " + "="*70)
        python_code.append("")
        
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                # Convert markdown to comments
                lines = cell.source.split('\n')
                python_code.append("")
                python_code.append("# " + "-"*70)
                for line in lines:
                    python_code.append("# " + line)
                python_code.append("# " + "-"*70)
                python_code.append("")
            
            elif cell.cell_type == 'code':
                python_code.append(cell.source)
                python_code.append("")
        
        with open(output_py_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(python_code))
        
        return True
    
    except Exception as e:
        print(f"Error converting notebook to Python: {e}")
        return False


def get_notebook_preview_html(notebook_path: str) -> str:
    """
    Generate a simple HTML preview of the notebook for embedding.
    
    Returns:
        HTML string
    """
    try:
        import subprocess
        
        result = subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'html', '--stdout', notebook_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return "<p>Could not generate preview</p>"
    
    except Exception as e:
        return f"<p>Error generating preview: {e}</p>"


def extract_chart_outputs(notebook_path: str, output_dir: str) -> List[str]:
    """
    Extract chart images from notebook outputs and save them as PNG files.
    
    Returns:
        List of paths to extracted images
    """
    image_paths = []
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        os.makedirs(output_dir, exist_ok=True)
        
        img_counter = 0
        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'outputs' in cell:
                for output in cell.outputs:
                    # Check for image data
                    if output.output_type == 'display_data' and 'data' in output:
                        if 'image/png' in output.data:
                            img_counter += 1
                            img_path = os.path.join(output_dir, f'chart_{img_counter}.png')
                            
                            # Decode base64 image data
                            import base64
                            img_data = output.data['image/png']
                            with open(img_path, 'wb') as img_file:
                                img_file.write(base64.b64decode(img_data))
                            
                            image_paths.append(img_path)
    
    except Exception as e:
        print(f"Error extracting charts: {e}")
    
    return image_paths


def get_execution_summary(metrics: Dict) -> str:
    """
    Generate a human-readable summary of the ML execution results.
    
    Returns:
        Formatted summary string
    """
    summary_lines = []
    
    if metrics.get('model_name'):
        summary_lines.append(f"**Model:** {metrics['model_name']}")
    
    # Classification metrics
    if metrics.get('accuracy') is not None:
        summary_lines.append(f"**Accuracy:** {metrics['accuracy']:.2%}")
    
    if metrics.get('precision') is not None:
        summary_lines.append(f"**Precision:** {metrics['precision']:.2%}")
    
    if metrics.get('recall') is not None:
        summary_lines.append(f"**Recall:** {metrics['recall']:.2%}")
    
    if metrics.get('f1_score') is not None:
        summary_lines.append(f"**F1-Score:** {metrics['f1_score']:.2%}")
    
    # Regression metrics
    if metrics.get('r2_score') is not None:
        summary_lines.append(f"**R² Score:** {metrics['r2_score']:.4f}")
    
    if metrics.get('mae') is not None:
        summary_lines.append(f"**Mean Absolute Error:** {metrics['mae']:.4f}")
    
    if metrics.get('rmse') is not None:
        summary_lines.append(f"**RMSE:** {metrics['rmse']:.4f}")
    
    # Data split info
    if metrics.get('training_samples') and metrics.get('testing_samples'):
        total = metrics['training_samples'] + metrics['testing_samples']
        summary_lines.append(f"**Training Samples:** {metrics['training_samples']} ({metrics['training_samples']/total:.0%})")
        summary_lines.append(f"**Testing Samples:** {metrics['testing_samples']} ({metrics['testing_samples']/total:.0%})")
    
    return "\n\n".join(summary_lines) if summary_lines else "No metrics available"
