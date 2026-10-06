"""Domain models for Mini Git."""

# [1차]: 데이터 클래스 정의 및 기본값 팩토리 함수를 가져옵니다.
# [2차]: 복잡한 생성자 코드 없이 데이터 상자를 손쉽게 찍어내기 위해 레고 블록 틀을 준비합니다.
from dataclasses import dataclass, field

# [1차]: 정적 타입 힌트를 위해 List, Dict, Optional 제네릭 타입을 가져옵니다.
# [2차]: 상자 안에 들어갈 물건의 종류(목록, 사전, 빈칸 허용)를 미리 명찰로 달아둡니다.
from typing import List, Dict, Optional


# [1차]: 불변 속성을 지닌 커밋 노드를 정의하는 dataclass 데코레이터입니다.
# [2차]: 커밋의 고유 정보들을 깔끔하게 포장하는 선물 세트 상자 틀을 만듭니다.
@dataclass
class Commit:
    """Represents an immutable commit node in the commit DAG.

    Attributes:
        hash: Unique commit identifier (hex string).
        message: Commit message describing the changes.
        author: Name of the commit author.
        timestamp: Epoch timestamp (float seconds) when the commit was created.
        parents: List of parent commit hashes (0 or more).
    """
    # [1차]: 커밋을 유일하게 식별하는 16진수 해시 문자열입니다.
    # [2차]: 전 세계에서 유일하게 주민등록번호처럼 부여되는 커밋의 고유 지문입니다.
    hash: str

    # [1차]: 개발자가 작성한 작업 변경 내용 설명 문자열입니다.
    # [2차]: 물건 상자 겉면에 매직으로 적어둔 "무슨 작업을 했는지" 설명 메모입니다.
    message: str

    # [1차]: 커밋을 생성한 사용자의 이름 문자열입니다.
    # [2차]: 서류 맨 밑에 도장을 쾅 찍은 작업자의 서명 명패입니다.
    author: str

    # [1차]: 1970년 1월 1일 이후 경과된 초 단위 부동소수점 타임스탬프입니다.
    # [2차]: 커밋이 탄생한 순간을 밀리초 단위까지 정확히 기록한 스톱워치 시간입니다.
    timestamp: float

    # [1차]: 0개 이상의 부모 커밋 해시들을 저장하는 동적 리스트(기본값은 빈 리스트)입니다.
    # [2차]: 이 커밋이 직전에 누구의 뒤를 이어받았는지 가리키는 족보상의 부모님 명단입니다.
    parents: List[str] = field(default_factory=list)


# [1차]: 메모리 세션 동안 저장소의 가변 상태를 추적하는 데이터 클래스입니다.
# [2차]: 현재 작업실 책상 위의 작업 상태(현재 사용자, 현재 브랜치)를 기록하는 메모판입니다.
@dataclass
class RepositoryState:
    """Represents the mutable state of the repository session."""
    # [1차]: INIT 명령어로 저장소가 초기화되었는지 여부를 나타내는 불리언 플래그입니다.
    # [2차]: 작업실 문을 열고 전등 스위치를 켰는지 확인하는 출입 스위치입니다.
    is_initialized: bool = False

    # [1차]: 현재 세션에서 작업 중인 작성자 이름(초기화 전에는 None)입니다.
    # [2차]: 현재 책상에 앉아서 코드를 작성하고 있는 개발자의 명찰입니다.
    current_author: Optional[str] = None

    # [1차]: 현재 HEAD가 가리키고 있는 활성 브랜치의 이름 문자열입니다.
    # [2차]: 현재 펼쳐놓고 작업 중인 도화지(브랜치)의 이름표입니다.
    head_branch: Optional[str] = None

    # [1차]: 브랜치 이름과 해당 브랜치의 최신 커밋 해시를 매핑하는 딕셔너리입니다.
    # [2차]: 각 도화지별로 가장 마지막에 그린 그림이 어디인지 가리키는 북마크 모음집입니다.
    branches: Dict[str, Optional[str]] = field(default_factory=dict)
