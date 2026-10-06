"""Script to generate high-quality architecture diagram images using matplotlib."""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# Setup font for Korean on Windows
plt.rc("font", family="Malgun Gothic")
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_dag_topological():
    """Diagram 1: Commit DAG and Topological Sort (Kahn's Algorithm)."""
    fig, ax = plt.subplots(figsize=(10, 7), dpi=200)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(0.5, 0.95, "[다이어그램 1] Git 커밋 그래프(DAG)와 위상 정렬(Topological Sort) 동작 원리",
            fontsize=15, fontweight="bold", ha="center", va="center", color="#1E293B")
    ax.text(0.5, 0.89, "Git 참조 방향: 자식 -> 부모  |  위상 정렬 탐색: 부모(in-degree=0)부터 선출력",
            fontsize=11, ha="center", va="center", color="#64748B")

    # Node coordinates
    # cA (Root) at top, cB and cC in middle, cD (Merge) at bottom
    nodes = {
        "cA": (0.5, 0.72, "cA (Root Commit)\n[in-degree: 0]\n최초 출력 (1순위)", "#3B82F6"),
        "cB": (0.28, 0.46, "cB (Branch-1)\n[in-degree: 1 -> 0]\n2순위 출력", "#10B981"),
        "cC": (0.72, 0.46, "cC (Branch-2)\n[in-degree: 1 -> 0]\n3순위 출력", "#10B981"),
        "cD": (0.5, 0.20, "cD (Merge Commit)\n[in-degree: 2 -> 0]\n최종 4순위 출력", "#8B5CF6")
    }

    # Draw nodes
    for name, (x, y, text, color) in nodes.items():
        box = patches.FancyBboxPatch(
            (x - 0.16, y - 0.08), 0.32, 0.15,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            ec=color, fc="#FFFFFF", lw=2.5, zorder=3
        )
        ax.add_patch(box)
        # Inner fill tint
        box_tint = patches.FancyBboxPatch(
            (x - 0.16, y - 0.08), 0.32, 0.15,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            ec="none", fc=color, alpha=0.12, zorder=3
        )
        ax.add_patch(box_tint)
        ax.text(x, y - 0.005, text, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B", zorder=4)

    # Draw DAG arrows (Topological flow: Parent -> Child)
    arrow_props = dict(arrowstyle="-|>", lw=2.2, color="#0EA5E9", mutation_scale=18, zorder=2)

    # cA -> cB
    ax.annotate("", xy=(0.33, 0.54), xytext=(0.45, 0.64), arrowprops=arrow_props)
    # cA -> cC
    ax.annotate("", xy=(0.67, 0.54), xytext=(0.55, 0.64), arrowprops=arrow_props)
    # cB -> cD
    ax.annotate("", xy=(0.45, 0.28), xytext=(0.33, 0.38), arrowprops=arrow_props)
    # cC -> cD
    ax.annotate("", xy=(0.55, 0.28), xytext=(0.67, 0.38), arrowprops=arrow_props)

    # Output queue banner at bottom
    queue_box = patches.FancyBboxPatch(
        (0.08, 0.03), 0.84, 0.08,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        ec="#475569", fc="#F1F5F9", lw=1.5
    )
    ax.add_patch(queue_box)
    ax.text(0.5, 0.07, "★ 최종 LOG 위상 정렬 순서 :  [ cA (Root) ] -> [ cB ] -> [ cC ] -> [ cD (Merge) ]\n(원칙 증명: 모든 부모 커밋은 자식 커밋보다 항상 먼저 출력됨)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#0F172A")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    path = os.path.join(OUTPUT_DIR, "architecture_1_dag_topological.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Saved: {path}")


def draw_inverted_index():
    """Diagram 2: Inverted Index Architecture vs Full Scan."""
    fig, ax = plt.subplots(figsize=(11, 7), dpi=200)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(0.5, 0.95, "[다이어그램 2] O(1) 초고속 역색인(Inverted Index) 검색 엔진 구조",
            fontsize=15, fontweight="bold", ha="center", va="center", color="#1E293B")
    ax.text(0.5, 0.89, "커밋 생성 시 단어와 작성자를 해시맵에 등록하여 O(N) 전체 순회(Full Scan)를 O(1)로 단축",
            fontsize=11, ha="center", va="center", color="#64748B")

    # Left Section: Raw Commit Stream
    left_bg = patches.FancyBboxPatch(
        (0.04, 0.14), 0.38, 0.68,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#CBD5E1", fc="#FFFFFF", lw=1.5
    )
    ax.add_patch(left_bg)
    ax.text(0.23, 0.77, "【 원본 커밋 데이터 저장소 】", ha="center", fontsize=11, fontweight="bold", color="#334155")

    commits_text = [
        ("c1", '"feat: user login module"\n(Author: Alice)', 0.65, "#3B82F6"),
        ("c2", '"fix: bug in login session"\n(Author: Bob)', 0.47, "#10B981"),
        ("c3", '"docs: user register guide"\n(Author: Alice)', 0.29, "#F59E0B")
    ]
    for cid, cdesc, cy, col in commits_text:
        cbox = patches.FancyBboxPatch(
            (0.07, cy - 0.06), 0.32, 0.12,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            ec=col, fc="#F8FAFC", lw=1.5
        )
        ax.add_patch(cbox)
        ax.text(0.09, cy, f"[{cid}]", fontsize=10, fontweight="bold", color=col, va="center")
        ax.text(0.15, cy, cdesc, fontsize=8.5, color="#1E293B", va="center")

    # Arrow from left to right
    ax.annotate("토큰 분리 & 색인\n(split + lower)", xy=(0.49, 0.50), xytext=(0.42, 0.50),
                arrowprops=dict(arrowstyle="->", lw=2, color="#64748B"),
                fontsize=9, ha="center", va="bottom", color="#475569")

    # Right Section: Inverted Index Tables
    right_bg = patches.FancyBboxPatch(
        (0.55, 0.14), 0.41, 0.68,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#CBD5E1", fc="#FFFFFF", lw=1.5
    )
    ax.add_patch(right_bg)
    ax.text(0.755, 0.77, "【 역색인 (Inverted Index) 해시 테이블 】", ha="center", fontsize=11, fontweight="bold", color="#334155")

    # Keyword Index Box
    ax.text(0.58, 0.70, "1. 키워드 색인 (Keyword Index)", fontsize=9.5, fontweight="bold", color="#2563EB")
    k_items = [
        ('"login"', '->  [ "c1", "c2" ]'),
        ('"user"', '->  [ "c1", "c3" ]'),
        ('"session"', '->  [ "c2" ]')
    ]
    ky = 0.63
    for k, v in k_items:
        ax.text(0.60, ky, f"• {k:<10} {v}", fontsize=9, color="#0F172A", family="monospace")
        ky -= 0.06

    # Author Index Box
    ax.text(0.58, 0.40, "2. 작성자 색인 (Author Index)", fontsize=9.5, fontweight="bold", color="#059669")
    a_items = [
        ('"alice"', '->  [ "c1", "c3" ]'),
        ('"bob"', '->  [ "c2" ]')
    ]
    ay = 0.33
    for k, v in a_items:
        ax.text(0.60, ay, f"• {k:<10} {v}", fontsize=9, color="#0F172A", family="monospace")
        ay -= 0.06

    # Comparison note banner
    banner = patches.FancyBboxPatch(
        (0.04, 0.03), 0.92, 0.07,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        ec="#0284C7", fc="#E0F2FE", lw=1.2
    )
    ax.add_patch(banner)
    ax.text(0.5, 0.065, "성능 비교 : 일반 검색(Full Scan) = O(N) 순회  vs  역색인(Inverted Index) = O(1) 즉시 해시 룩업",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#0369A1")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    path = os.path.join(OUTPUT_DIR, "architecture_2_inverted_index.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Saved: {path}")


def draw_bfs_path():
    """Diagram 3: Undirected BFS Shortest Path with Tie-Breaking."""
    fig, ax = plt.subplots(figsize=(10, 7), dpi=200)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(0.5, 0.95, "[다이어그램 3] 무방향 BFS 최단 경로(Shortest Path) & 사전순 타이 브레이킹",
            fontsize=15, fontweight="bold", ha="center", va="center", color="#1E293B")
    ax.text(0.5, 0.89, "부모-자식 연결을 양방향 간선으로 간주하여 최소 홉 탐색 후 동률 시 사전순 최소 선택",
            fontsize=11, ha="center", va="center", color="#64748B")

    # Graph Nodes
    # c_start (top), c_nodeB (left), c_nodeA (right), c_end (bottom)
    pts = {
        "start": (0.5, 0.73, "c_start\n(출발 노드)", "#2563EB"),
        "nodeB": (0.28, 0.46, "c_nodeB\n(1홉 도달)", "#EA580C"),
        "nodeA": (0.72, 0.46, "c_nodeA\n(1홉 도달)", "#16A34A"),
        "end": (0.5, 0.20, "c_end\n(도착 노드)", "#9333EA")
    }

    for k, (x, y, label, col) in pts.items():
        circ = patches.Circle((x, y), 0.07, ec=col, fc="#FFFFFF", lw=2.5, zorder=3)
        ax.add_patch(circ)
        circ_tint = patches.Circle((x, y), 0.07, ec="none", fc=col, alpha=0.15, zorder=3)
        ax.add_patch(circ_tint)
        ax.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold", color="#1E293B", zorder=4)

    # Undirected bidirectional lines
    line_props = dict(color="#64748B", lw=2.5, zorder=2)
    ax.plot([0.5, 0.28], [0.73, 0.46], **line_props)
    ax.plot([0.5, 0.72], [0.73, 0.46], **line_props)
    ax.plot([0.28, 0.5], [0.46, 0.20], **line_props)
    ax.plot([0.72, 0.5], [0.46, 0.20], **line_props)

    # Edge labels (hops)
    ax.text(0.36, 0.62, "무방향 1홉", fontsize=9, fontweight="bold", color="#64748B")
    ax.text(0.60, 0.62, "무방향 1홉", fontsize=9, fontweight="bold", color="#64748B")
    ax.text(0.36, 0.31, "무방향 2홉", fontsize=9, fontweight="bold", color="#64748B")
    ax.text(0.60, 0.31, "무방향 2홉", fontsize=9, fontweight="bold", color="#64748B")

    # Tie break panel
    tb_box = patches.FancyBboxPatch(
        (0.08, 0.03), 0.84, 0.11,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        ec="#15803D", fc="#F0FDF4", lw=1.5
    )
    ax.add_patch(tb_box)
    tb_text = (
        "【 동일 거리(2홉) 후보군 문자열 비교 (Tie-Breaking) 】\n"
        "• 경로 1 : 'c_start->c_nodeB->c_end'\n"
        "• 경로 2 : 'c_start->c_nodeA->c_end'  ★ 사전순(Lexicographical)으로 더 작으므로 최종 채택!"
    )
    ax.text(0.5, 0.085, tb_text, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#166534")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    path = os.path.join(OUTPUT_DIR, "architecture_3_bfs_shortest_path.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Saved: {path}")


def draw_merge_sort():
    """Diagram 4: Custom Stable Merge Sort (Divide & Conquer)."""
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=200)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(0.5, 0.95, "[다이어그램 4] 내장 API 배제 순수 안정 병합 정렬 (Merge Sort) 분할 정복",
            fontsize=15, fontweight="bold", ha="center", va="center", color="#1E293B")
    ax.text(0.5, 0.89, "sorted(), list.sort() 금지 -> 항상 O(N log N) 보장 & 키 동률 시 입력 순서 보존(Stable)",
            fontsize=11, ha="center", va="center", color="#64748B")

    # Divide Phase (Downwards)
    ax.text(0.08, 0.78, "【 1단계: 분할 (Divide) 】", fontsize=11, fontweight="bold", color="#0284C7")
    ax.text(0.08, 0.74, "원소 수가 1개 이하가 될 때까지 중앙(mid)을 기준으로 재귀 이등분", fontsize=9, color="#64748B")

    # Tree Nodes
    def draw_box(x, y, w, h, text, col="#0284C7"):
        b = patches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                   ec=col, fc="#FFFFFF", lw=1.8, zorder=3)
        ax.add_patch(b)
        b_tint = patches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        ec="none", fc=col, alpha=0.1, zorder=3)
        ax.add_patch(b_tint)
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A", zorder=4)

    # Root
    draw_box(0.5, 0.68, 0.32, 0.05, "[ 38,  27,  43,   3,   9,  82 ]")

    # Level 1
    draw_box(0.32, 0.58, 0.20, 0.05, "[ 38, 27, 43 ]")
    draw_box(0.68, 0.58, 0.20, 0.05, "[ 3, 9, 82 ]")
    ax.annotate("", xy=(0.32, 0.61), xytext=(0.45, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color="#94A3B8"))
    ax.annotate("", xy=(0.68, 0.61), xytext=(0.55, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color="#94A3B8"))

    # Level 2 (Base case size 1)
    leaves = [(0.20, "[ 38 ]"), (0.32, "[ 27 ]"), (0.44, "[ 43 ]"),
              (0.56, "[ 3 ]"), (0.68, "[ 9 ]"), (0.80, "[ 82 ]")]
    for lx, lt in leaves:
        draw_box(lx, 0.48, 0.09, 0.045, lt, col="#64748B")

    # Conquer & Combine Phase (Upwards)
    ax.text(0.08, 0.38, "【 2단계: 정렬 및 병합 (Conquer & Combine) 】", fontsize=11, fontweight="bold", color="#16A34A")
    ax.text(0.08, 0.34, "투 포인터(Two-Pointers) 비교 -> 키 동률 시 왼쪽 원소 우선 선택으로 안정성(Stability) 100% 보장",
            fontsize=9, color="#64748B")

    # Merged pairs
    draw_box(0.32, 0.26, 0.22, 0.05, "[ 27, 38, 43 ] (정렬 병합)", col="#16A34A")
    draw_box(0.68, 0.26, 0.22, 0.05, "[ 3, 9, 82 ] (정렬 병합)", col="#16A34A")
    ax.annotate("", xy=(0.32, 0.29), xytext=(0.26, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5, color="#16A34A"))
    ax.annotate("", xy=(0.68, 0.29), xytext=(0.74, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5, color="#16A34A"))

    # Final Merged
    draw_box(0.5, 0.14, 0.36, 0.055, "[ 3,  9,  27,  38,  43,  82 ] (완료)", col="#7C3AED")
    ax.annotate("", xy=(0.45, 0.17), xytext=(0.35, 0.23), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7C3AED"))
    ax.annotate("", xy=(0.55, 0.17), xytext=(0.65, 0.23), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7C3AED"))

    # Bottom summary banner
    ms_box = patches.FancyBboxPatch(
        (0.05, 0.02), 0.90, 0.065,
        boxstyle="round,pad=0.01,rounding_size=0.015",
        ec="#475569", fc="#F1F5F9", lw=1.2
    )
    ax.add_patch(ms_box)
    ax.text(0.5, 0.052, "복잡도: 최선/평균/최악 O(N log N) | 공간 복잡도: O(N) | 내장 API: sorted() 0회, list.sort() 0회",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0F172A")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    path = os.path.join(OUTPUT_DIR, "architecture_4_merge_sort.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Saved: {path}")


if __name__ == "__main__":
    draw_dag_topological()
    draw_inverted_index()
    draw_bfs_path()
    draw_merge_sort()
