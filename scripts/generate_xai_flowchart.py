import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Box properties
box_style = "round,pad=0.3,rounding_size=0.1"
props_blue = dict(boxstyle=box_style, facecolor='#4da6ff', edgecolor='blue', alpha=0.9)
props_green = dict(boxstyle=box_style, facecolor='#66cc66', edgecolor='green', alpha=0.9)
props_orange = dict(boxstyle=box_style, facecolor='#ffb366', edgecolor='#e67300', alpha=0.9)
props_purple = dict(boxstyle=box_style, facecolor='#b366ff', edgecolor='#7300e6', alpha=0.9)

# Define nodes (x, y, text, props)
nodes = {
    'A': (5, 5, 'Nhập thông tin\nnhân viên', props_blue),
    'B': (5, 4, 'Mô hình AI\n(XGBoost / RandomForest)', props_blue),
    'C': (2, 2.5, 'Kết quả dự đoán\nNguy cơ nghỉ việc (%)', props_orange),
    'D': (8, 2.5, 'Công cụ Explainable AI\n(SHAP)', props_purple),
    'E': (8, 1, 'Phân tích mức độ\nảnh hưởng của từng đặc trưng', props_purple),
    'F': (5, 1, 'Giao diện\nNgười quản lý', props_green)
}

# Draw nodes
for key, (x, y, text, props) in nodes.items():
    ax.text(x, y, text, size=11, ha='center', va='center', bbox=props, fontweight='bold', color='white')

# Draw arrows
arrow_props = dict(facecolor='black', edgecolor='black', width=1.5, headwidth=8, headlength=10, shrink=0.08)

ax.annotate('', xy=(5, 4.3), xytext=(5, 4.8), arrowprops=arrow_props) # A -> B
ax.annotate('', xy=(2.5, 2.8), xytext=(4.5, 3.7), arrowprops=arrow_props) # B -> C
ax.annotate('', xy=(7.5, 2.8), xytext=(5.5, 3.7), arrowprops=arrow_props) # B -> D
ax.annotate('', xy=(8, 1.4), xytext=(8, 2.1), arrowprops=arrow_props) # D -> E
ax.annotate('', xy=(5.5, 1), xytext=(6.5, 1), arrowprops=arrow_props) # E -> F
ax.annotate('', xy=(4.5, 1), xytext=(2, 2.1), arrowprops=arrow_props) # C -> F

plt.title('Hình 2.6. Quy trình Explainable AI trong hệ thống', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('assets/xai_flowchart.png', dpi=300)
plt.close()
print('Generated assets/xai_flowchart.png')
