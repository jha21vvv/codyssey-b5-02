"""CLI REPL interface and command dispatcher for Mini Git."""

# [1차]: 표준 시스템 및 입출력 모듈을 가져옵니다.
# [2차]: 터미널 운영체제와 소통하기 위한 마이크를 준비합니다.
import sys

# [1차]: 셸 스타일의 따옴표 및 공백 파싱을 제공하는 shlex 모듈을 가져옵니다.
# [2차]: 큰따옴표로 감싼 긴 문장("Add login feature")을 단어 하나로 똑똑하게 묶어주는 통역기입니다.
import shlex

# [1차]: 타임스탬프를 읽기 쉬운 로컬 일시 포맷으로 변환하기 위해 time 모듈을 가져옵니다.
# [2차]: 초 단위 숫자를 "2026-10-06 12:00:00" 같은 달력 날짜로 바꿔주는 손목시계입니다.
import time

# [1차]: 타입 어노테이션을 위한 표준 타이핑 심볼을 가져옵니다.
# [2차]: 함수의 입력과 출력 상자에 라벨을 붙여줍니다.
from typing import Optional

# [1차]: 비즈니스 로직을 수행하는 MiniGitRepository 클래스를 가져옵니다.
# [2차]: 명령을 실제로 수행해 줄 작업실 총괄 지배인을 불러옵니다.
from minigit.repository import MiniGitRepository

# [1차]: 커밋 도메인 모델 데이터 클래스를 가져옵니다.
# [2차]: 커밋 서류 양식을 가져옵니다.
from minigit.models import Commit


# [1차]: 커밋의 해시, 작성자, 생성일시, 부모, 메시지를 식별 가능하도록 다중 라인 문자열로 포맷팅합니다.
# [2차]: 서류 상자 속 커밋 정보를 영수증처럼 깔끔하게 인쇄해 주는 프린터기입니다.
def format_commit(commit: Commit) -> str:
    """Formats a single commit for display.
    Guarantees hash, author, timestamp, message are identifiable.
    """
    # [1차]: 부동소수점 타임스탬프를 "YYYY-MM-DD HH:MM:SS" 형식의 문자열로 변환합니다.
    # [2차]: 컴퓨터용 밀리초 시간을 사람이 읽을 수 있는 달력 시간으로 번역합니다.
    ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.timestamp))
    # [1차]: 부모 해시가 있으면 쉼표로 연결하고 없으면 (root)로 표시합니다.
    # [2차]: 부모님이 있으면 족보에 쉼표로 이어 붙이고, 최초 커밋이면 (뿌리)라고 명시합니다.
    parents_str = ", ".join(commit.parents) if commit.parents else "(root)"
    # [1차]: 요구사항에서 명시한 필수 식별 정보(hash, author, date, message) 라인들을 조립합니다.
    # [2차]: 커밋 번호, 작성자 명찰, 시간표, 부모님, 작업 설명을 편지지에 가지런히 적습니다.
    lines = [
        f"commit {commit.hash}",
        f"Author:    {commit.author}",
        f"Date:      {ts_str} ({commit.timestamp:.2f})",
        f"Parents:   {parents_str}",
        f"    {commit.message}"
    ]
    # [1차]: 개행 문자(\n)로 조인하여 단일 출력 문자열을 생성합니다.
    # [2차]: 줄바꿈을 적용해 한 장의 단정한 영수증으로 완성합니다.
    return "\n".join(lines)


# [1차]: 사용자의 CLI 입력을 파싱하고 각 커맨드 핸들러로 라우팅하는 컨트롤러 클래스입니다.
# [2차]: 사용자가 터미널 창구에서 외치는 말을 듣고 담당 부서로 연결해 주는 친절한 안내 데스크입니다.
class MiniGitCLI:
    """REPL CLI controller."""

    # [1차]: CLI 인스턴스를 초기화하며 리포지토리 의존성을 주입받거나 기본 생성합니다.
    # [2차]: 안내 데스크에 앉아 작업실 총괄 지배인과 무전기를 연결합니다.
    def __init__(self, repo: Optional[MiniGitRepository] = None, storage_path: Optional[str] = None) -> None:
        # [1차]: 주입된 리포지토리가 있으면 사용하고 없으면 새 MiniGitRepository를 생성합니다.
        # [2차]: 지정된 작업실이 있으면 그곳과 연결하고 없으면 새 작업실을 바로 차립니다.
        self.repo = repo if repo is not None else MiniGitRepository(storage_path=storage_path)

    # [1차]: 입력된 한 줄의 명령 문자열을 파싱하고 실행하여 결과 문자열을 반환합니다.
    # [2차]: 손님이 건넨 한 줄의 요청 쪽지를 읽고 알맞은 업무를 처리한 후 결과지를 건네줍니다.
    def execute_line(self, line: str) -> Optional[str]:
        """Parses and executes a single CLI command string."""
        # [1차]: 입력 라인의 앞뒤 공백을 제거합니다.
        # [2차]: 쪽지 양옆의 빈 공간을 가위로 오려냅니다.
        line = line.strip()
        # [1차]: 내용이 없는 빈 줄이면 None을 반환합니다.
        # [2차]: 빈 쪽지가 들어오면 아무 말 없이 침묵합니다.
        if not line:
            return None

        # [1차]: 따옴표 처리를 포함한 셸 토큰 분리를 시도합니다.
        # [2차]: 따옴표로 감싸진 단어들을 훼손 없이 한 덩어리로 안전하게 자릅니다.
        try:
            tokens = shlex.split(line)
        # [1차]: 닫히지 않은 따옴표 등 파싱 오류 시 표준 에러 메시지를 반환합니다.
        # [2차]: 따옴표 짝이 안 맞으면 문법 오류라고 정중히 알립니다.
        except ValueError as e:
            return f"Invalid args: parsing quotes failed ({e})"

        # [1차]: 파싱 결과 토큰이 비어있으면 None을 반환합니다.
        # [2차]: 쪼개고 났더니 남은 단어가 없으면 통과합니다.
        if not tokens:
            return None

        # [1차]: 첫 번째 토큰인 명령어 키워드를 대문자로 정규화하여 대소문자 구분을 없앱니다.
        # [2차]: 손님이 소문자(init)로 쓰든 대문자(INIT)로 쓰든 똑같이 큰 소리로 알아듣습니다.
        cmd = tokens[0].upper()
        # [1차]: 첫 번째 명령어를 제외한 나머지 인자 토큰들을 슬라이싱합니다.
        # [2차]: 명령어 뒤에 딸려온 세부 준비물 목록을 챙깁니다.
        args = tokens[1:]

        # [1차]: 비즈니스 로직 실행 및 예외 포착 블록입니다.
        # [2차]: 실제 작업 지시를 내리고 혹시 모를 문제를 방어하는 안전망입니다.
        try:
            # [1차]: INIT 명령어 분기: 저장소 초기화 및 사용자 설정을 수행합니다.
            # [2차]: "작업실 개관" 명령을 받아 새 작업실을 준비합니다.
            if cmd == "INIT":
                # [1차]: 인자 수가 정확히 1개가 아닌 경우 에러를 반환합니다.
                # [2차]: 작업자 이름이 빠졌거나 너무 많으면 안내문을 띄웁니다.
                if len(args) != 1:
                    return "Invalid args: INIT requires <user_name>"
                # [1차]: 저장소 init 메서드를 호출하고 결과 문자열을 반환합니다.
                # [2차]: 작업실 문을 열고 작업자 명찰을 등록합니다.
                return self.repo.init(args[0])

            # [1차]: BRANCH 명령어 분기: 새로운 브랜치를 생성합니다.
            # [2차]: "새 도화지 복사" 명령을 받아 도화지 책갈피를 만듭니다.
            elif cmd == "BRANCH":
                # [1차]: 브랜치 이름 인자가 정확히 1개인지 검증합니다.
                # [2차]: 도화지 이름이 1개가 아니면 안내문을 돌려줍니다.
                if len(args) != 1:
                    return "Invalid args: BRANCH requires <branch_name>"
                # [1차]: 리포지토리의 branch 메서드를 호출합니다.
                # [2차]: 지배인에게 새 도화지 생성을 지시합니다.
                return self.repo.branch(args[0])

            # [1차]: SWITCH 명령어 분기: 활성 HEAD 브랜치를 변경합니다.
            # [2차]: "도화지 교체" 명령을 받아 작업 도화지를 바꿉니다.
            elif cmd == "SWITCH":
                # [1차]: 대상 브랜치명 인자가 1개인지 검증합니다.
                # [2차]: 바꿀 도화지 이름이 명확한지 확인합니다.
                if len(args) != 1:
                    return "Invalid args: SWITCH requires <branch_name>"
                # [1차]: 리포지토리의 switch 메서드를 호출합니다.
                # [2차]: 지배인에게 도화지를 바꿔달라고 요청합니다.
                return self.repo.switch(args[0])

            # [1차]: COMMIT 명령어 분기: 신규 커밋을 생성합니다.
            # [2차]: "작업 저장" 명령을 받아 현재 그림을 책에 철합니다.
            elif cmd == "COMMIT":
                # [1차]: 커밋 메시지 인자가 1개인지 검증합니다.
                # [2차]: 작업 메모가 정확히 들어왔는지 확인합니다.
                if len(args) != 1:
                    return "Invalid args: COMMIT requires <message>"
                # [1차]: 리포지토리 commit을 호출하여 커밋 생성 알림 메시지를 반환합니다.
                # [2차]: 지배인이 새 그림을 저장하고 도장 번호를 알려줍니다.
                _, msg = self.repo.commit(args[0])
                return msg

            # [1차]: LOG 명령어 분기: 위상 정렬 또는 정렬 옵션에 따른 커밋 로그를 출력합니다.
            # [2차]: "작업 이력 보기" 명령을 받아 지금까지의 그림 목록을 보여줍니다.
            elif cmd == "LOG":
                # [1차]: 정렬 기준 변수를 None(위상 정렬 기본값)으로 초기화합니다.
                # [2차]: 별도 정렬 기준이 없으면 기본 족보 순서로 설정합니다.
                sort_by = None
                # [1차]: 옵션 인자가 1개 전달된 경우 파싱합니다.
                # [2차]: 손님이 특별한 정렬 기준을 요구했는지 확인합니다.
                if len(args) == 1:
                    opt = args[0]
                    # [1차]: 옵션이 --sort-by= 로 시작하는지 검증합니다.
                    # [2차]: 정렬 옵션 규칙 표기법을 준수했는지 확인합니다.
                    if opt.startswith("--sort-by="):
                        val = opt.split("=", 1)[1].strip()
                        # [1차]: date 또는 author 값만 허용합니다.
                        # [2차]: 날짜순이나 작성자순 외의 이상한 값은 차단합니다.
                        if val not in ("date", "author"):
                            return "Invalid args: --sort-by must be date or author"
                        sort_by = val
                    else:
                        return "Invalid args: unknown option for LOG"
                # [1차]: 옵션 인자가 2개 이상이면 에러를 반환합니다.
                # [2차]: 정렬 옵션을 너무 많이 붙이면 퇴짜를 놓습니다.
                elif len(args) > 1:
                    return "Invalid args: LOG accepts at most one --sort-by option"

                # [1차]: 리포지토리의 log 메서드를 호출하여 정렬된 커밋 목록을 가져옵니다.
                # [2차]: 지배인에게 요청한 순서대로 커밋 목록을 받아옵니다.
                commits = self.repo.log(sort_by=sort_by)
                # [1차]: 커밋이 하나도 없으면 안내 메시지를 반환합니다.
                # [2차]: 저장된 그림이 없으면 비어있다고 알립니다.
                if not commits:
                    return "No commits found."
                # [1차]: 각 커밋을 format_commit으로 예쁘게 포맷팅하여 이중 개행으로 결합합니다.
                # [2차]: 각 커밋 영수증을 보기 좋게 두 줄 띄우고 하나로 묶어 출력합니다.
                return "\n\n".join(format_commit(c) for c in commits)

            # [1차]: PATH 명령어 분기: 두 커밋 간 무방향 최단 경로를 탐색합니다.
            # [2차]: "최단 길 찾기" 명령을 받아 두 정거장 사이의 가장 빠른 길을 찾습니다.
            elif cmd == "PATH":
                # [1차]: 시작 및 종료 커밋 해시 2개 인자가 필수입니다.
                # [2차]: 출발역과 도착역 2개가 정확히 필요합니다.
                if len(args) != 2:
                    return "Invalid args: PATH requires <commit1> <commit2>"
                # [1차]: 리포지토리의 path 메서드를 호출합니다.
                # [2차]: 내비게이션을 돌려 최단 경로를 탐색합니다.
                path = self.repo.path(args[0], args[1])
                # [1차]: 연결 경로가 없으면 'No path'를 출력합니다.
                # [2차]: 가는 길이 없으면 'No path'라고 보고합니다.
                if path is None:
                    return "No path"
                # [1차]: 경로 해시 리스트를 ' -> ' 화살표로 연결하여 반환합니다.
                # [2차]: 'c1 -> c2 -> c3'처럼 길 안내 화살표로 연결해 출력합니다.
                return " -> ".join(path)

            # [1차]: ANCESTORS 명령어 분기: 특정 커밋의 모든 조상을 탐색합니다.
            # [2차]: "조상님 찾기" 명령을 받아 모든 선조 명단을 조사합니다.
            elif cmd == "ANCESTORS":
                # [1차]: 대상 커밋 해시 인자가 1개인지 검증합니다.
                # [2차]: 누구의 조상을 찾을지 번호 1개를 확인합니다.
                if len(args) != 1:
                    return "Invalid args: ANCESTORS requires <commit_hash>"
                # [1차]: 리포지토리의 ancestors 메서드를 호출합니다.
                # [2차]: 지배인에게 모든 조상 서류 조사를 요청합니다.
                ancestors = self.repo.ancestors(args[0])
                # [1차]: 조상이 없으면 안내 문구를 반환합니다.
                # [2차]: 최초 커밋이라 조상이 없으면 없다고 알립니다.
                if not ancestors:
                    return "No ancestors."
                # [1차]: 조상 커밋들을 포맷팅하여 반환합니다.
                # [2차]: 찾아낸 모든 조상님 영수증을 출력합니다.
                return "\n\n".join(format_commit(c) for c in ancestors)

            # [1차]: SEARCH 명령어 분기: 역색인 기반 키워드 또는 작성자 검색을 수행합니다.
            # [2차]: "색인 검색" 명령을 받아 O(1) 초고속으로 일치하는 문서를 찾습니다.
            elif cmd == "SEARCH":
                # [1차]: 검색 인자가 1개인지 검증합니다.
                # [2차]: 찾을 단어나 작성자 명찰 1개를 확인합니다.
                if len(args) != 1:
                    return "Invalid args: SEARCH requires <keyword> or --author=<name>"
                target = args[0]
                # [1차]: --author= 옵션 형식으로 들어온 경우 작성자 역색인을 조회합니다.
                # [2차]: 작가 이름으로 찾는 검색 요청을 처리합니다.
                if target.startswith("--author="):
                    author_name = target.split("=", 1)[1].strip()
                    # [1차]: 작성자명이 비어있을 경우 유효성 검사 에러를 반환합니다.
                    # [2차]: 찾을 작가 이름을 적지 않았으면 거절합니다.
                    if not author_name:
                        return "Invalid args: --author requires a name"
                    commits = self.repo.search_author(author_name)
                # [1차]: 일반 키워드로 들어온 경우 키워드 역색인을 조회합니다.
                # [2차]: 단어로 찾는 검색 요청을 처리합니다.
                else:
                    commits = self.repo.search_keyword(target)

                # [1차]: 검색 결과가 없으면 안내 메시지를 반환합니다.
                # [2차]: 일치하는 그림이 없으면 비어있음을 알립니다.
                if not commits:
                    return "No commits found."
                # [1차]: 검색된 커밋 목록을 포맷팅하여 반환합니다.
                # [2차]: 찾아낸 커밋 영수증들을 출력합니다.
                return "\n\n".join(format_commit(c) for c in commits)

            # [1차]: EXIT 또는 QUIT 명령어 분기: REPL 종료 플래그 문자열을 반환합니다.
            # [2차]: 손님이 '퇴장'을 선언하면 작별 인사를 준비합니다.
            elif cmd in ("EXIT", "QUIT"):
                return "BYE"

            # [1차]: 알 수 없는 명령어 입력 시 표준 에러 메시지를 반환합니다.
            # [2차]: 모르는 명령어가 들어오면 올바르지 않은 명령이라고 안내합니다.
            else:
                return f"Invalid args: unknown command '{tokens[0]}'"

        # [1차]: 초기화되지 않은 저장소 접근 등 런타임 에러를 문자열로 변환하여 출력합니다.
        # [2차]: 작업실 미개관 등 운영 에러를 사용자에게 친절히 설명합니다.
        except RuntimeError as e:
            return str(e)
        # [1차]: 존재하지 않는 브랜치/커밋 키 조회 실패 시 예외 메시지를 반환합니다.
        # [2차]: 없는 도화지나 번호표를 요구했을 때 그 이유를 안내합니다.
        except KeyError as e:
            err_msg = str(e).strip("'\"")
            return err_msg
        # [1차]: 인자 형식 불일치 등 유효성 검증 에러를 문자열로 변환합니다.
        # [2차]: 입력값 규격 위반 사항을 사용자에게 알립니다.
        except ValueError as e:
            return str(e)

    # [1차]: 사용자와 대화형으로 명령을 주고받는 대화형 REPL 루프 진입점입니다.
    # [2차]: 손님이 나가기 전까지 끊임없이 주문을 받고 응대하는 카운터 안내원입니다.
    def run_repl(self) -> None:
        """Starts the interactive CLI REPL session."""
        # [1차]: 프로그램 시작 안내 배너를 출력합니다.
        # [2차]: "Mini Git 창구에 오신 것을 환영합니다" 간판을 켭니다.
        print("Mini Git CLI v1.0.0 (Type 'exit' or 'quit' to close)")
        # [1차]: 기존에 저장된 레포지토리가 복원되었으면 안내 메시지를 출력합니다.
        # [2차]: 이전에 작업하던 서류가 남아있다면 현재 작업자와 도화지 상태를 알려줍니다.
        if self.repo.is_initialized():
            print(f"[*] Loaded repository for '{self.repo.state.current_author}' on branch '{self.repo.state.head_branch}'")
        # [1차]: 사용자가 exit 또는 Ctrl+C를 누를 때까지 무한 반복 루프를 돕니다.
        # [2차]: 손님이 퇴장하기 전까지 계속 대기하며 주문을 받습니다.
        while True:
            # [1차]: 사용자 입력을 표준 입력에서 받아옵니다.
            # [2차]: "mini-git> " 프롬프트 명찰을 띄우고 손님의 입력을 기다립니다.
            try:
                line = input("mini-git> ")
            # [1차]: EOF(Ctrl+D/Ctrl+Z) 또는 인터럽트(Ctrl+C) 발생 시 안전하게 탈출합니다.
            # [2차]: 손님이 급하게 창구를 닫고 떠나면 공손히 배웅합니다.
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Mini Git.")
                break

            # [1차]: 입력된 라인을 실행 엔진에 전달하여 처리 결과를 받습니다.
            # [2차]: 주문받은 내용을 처리 기계에 넣고 결과지를 뽑아옵니다.
            output = self.execute_line(line)
            # [1차]: 종료 플래그("BYE")가 반환되면 루프를 종료합니다.
            # [2차]: 작별 인사 카드가 나오면 카운터를 마감합니다.
            if output == "BYE":
                print("Exiting Mini Git.")
                break
            # [1차]: 결과가 존재하면 콘솔 화면에 출력합니다.
            # [2차]: 처리된 결과 영수증을 손님에게 건넵니다.
            elif output is not None:
                print(output)
