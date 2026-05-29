import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Path configurations
OUTPUT_DIR = r"C:\Users\ngo24\.gemini\antigravity-ide\brain\8e1f8058-fd41-483e-8d62-04051ecc6a1d\assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_confusion_matrix():
    # Data
    # [[TN, FP], [FN, TP]]
    cm = np.array([[35, 0], [0, 6]])
    labels = ['Predict Active', 'Predict Resigned']
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Active (0)', 'Resigned (1)'],
                yticklabels=['Actual Active (0)', 'Actual Resigned (1)'],
                annot_kws={"size": 16})
    plt.title('AI Attrition Prediction - Confusion Matrix', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'), dpi=300)
    plt.close()

def generate_metrics_chart():
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    values = [1.0, 1.0, 1.0, 1.0, 1.0]
    
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=metrics, y=values, palette="viridis")
    
    for i, v in enumerate(values):
        ax.text(i, v - 0.05, f"{v*100:.0f}%", ha='center', color='white', fontweight='bold', fontsize=12)
        
    plt.ylim(0, 1.1)
    plt.title('AI Model Evaluation Metrics', fontsize=14)
    plt.ylabel('Score')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'ai_metrics_bar.png'), dpi=300)
    plt.close()

def generate_feature_importance():
    features = ['late_count', 'monthly_late_trend', 'task_completion_rate', 'pending_task_rate', 'job_satisfaction']
    importances = [0.2378, 0.1658, 0.1564, 0.1284, 0.0638]
    
    # Reverse to show highest at the top
    features.reverse()
    importances.reverse()
    
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=importances, y=features, palette="rocket")
    
    for i, v in enumerate(importances):
        ax.text(v + 0.005, i, f"{v:.4f}", va='center', fontweight='bold', fontsize=10)
        
    plt.xlim(0, max(importances) + 0.05)
    plt.title('Top 5 Feature Importances (RandomForest)', fontsize=14)
    plt.xlabel('Importance Score')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'feature_importance.png'), dpi=300)
    plt.close()

def generate_performance_benchmark():
    functions = ['Login', 'Dashboard Loading', 'AI Prediction', 'Database Query']
    latencies = [45, 120, 45, 25] # in ms
    
    # Reverse for better display
    functions.reverse()
    latencies.reverse()
    
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=latencies, y=functions, palette="crest")
    
    for i, v in enumerate(latencies):
        ax.text(v + 2, i, f"{v} ms", va='center', fontweight='bold', fontsize=11)
        
    plt.xlim(0, max(latencies) + 20)
    plt.title('System Performance Benchmark (Latency in ms)', fontsize=14)
    plt.xlabel('Response Time (ms)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'performance_benchmark.png'), dpi=300)
    plt.close()

if __name__ == '__main__':
    generate_confusion_matrix()
    generate_metrics_chart()
    generate_feature_importance()
    generate_performance_benchmark()
    print("Charts generated successfully.")
