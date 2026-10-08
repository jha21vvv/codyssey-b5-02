"""Inverted Index module for Mini Git.

Provides O(1) keyword and author lookup to avoid O(N) full-table scans.
"""

# [1차]: 딕셔너리, 리스트, 집합을 위한 타입 힌팅 심볼들을 가져옵니다.
# [2차]: 색인 도서관의 책장(Dict), 목록표(List), 중복 방지 도장(Set)을 마련합니다.
from typing import Dict, List, Set

# [1차]: 커밋 도메인 모델 클래스를 가져옵니다.
# [2차]: 인덱싱 대상이 되는 커밋 서류 양식을 불러옵니다.
from minigit.models import Commit


# [1차]: 키워드 및 작성자별 커밋 해시 역색인을 관리하는 클래스입니다.
# [2차]: 백과사전 맨 뒷장에 단어와 작성자 이름으로 페이지 번호를 찾아주는 색인 관리소입니다.
class InvertedIndex:
    """Manages inverted indexes for commit keywords and authors."""

    # [1차]: 색인 저장용 딕셔너리들을 초기화하는 생성자입니다.
    # [2차]: 비어있는 색인 노트 두 권(단어 색인, 사람 색인)을 책상에 펼칩니다.
    def __init__(self) -> None:
        # [1차]: 소문자 정규화된 토큰 문자열을 키로, 커밋 해시 목록을 값으로 매핑하는 딕셔너리입니다.
        # [2차]: 'login'이라는 단어가 적힌 포스트잇에 관련 커밋 번호들을 줄줄이 적어둘 파일철입니다.
        self._keyword_index: Dict[str, List[str]] = {}

        # [1차]: 소문자 정규화된 작성자 이름을 키로, 커밋 해시 목록을 값으로 매핑하는 딕셔너리입니다.
        # [2차]: 'alice'라는 작가 이름 아래에 그 작가가 쓴 작품 번호들을 모아둘 파일철입니다.
        self._author_index: Dict[str, List[str]] = {}

    # [1차]: 객체 상태와 무관하게 문자열 토큰화만 수행하는 정적 메서드 데코레이터입니다.
    # [2차]: 외부 문서가 들어오면 단어 단위로 싹둑 잘라주는 전용 커터 칼 도구입니다.
    # 색인화하기 위해, 일단 짤라서 색인용으로 만든후 여기에 만족하는지 다시 계산 시키는 방식
    @staticmethod
    def tokenize(message: str) -> List[str]:
        """Extracts normalized lowercase tokens split by whitespace."""
        # [1차]: 문자열 앞뒤 공백을 제거한 후 공백 문자를 기준으로 분할하여 단어 리스트를 생성합니다.
        # [2차]: 문장 앞뒤의 빈 공간을 털어내고 띄어쓰기마다 단어를 싹둑 자릅니다.
        tokens = message.strip().split()

        # [1차]: 비어있지 않은 각 토큰을 소문자로 변환하여 리스트 컴프리헨션으로 반환합니다.
        # [2차]: 대문자 소문자 섞인 단어들을 모두 소문자로 가지런히 다듬어 바구니에 담습니다.
        return [token.lower() for token in tokens if token]

    # [1차]: 새로 생성된 커밋을 키워드 색인 및 작성자 색인에 등록하는 메서드입니다.
    # [2차]: 새 커밋 서류가 도착했을 때 색인 노트 두 권에 해당 커밋 번호를 적어넣는 작업입니다.
    def add_commit(self, commit: Commit) -> None:
        """Indexes a new commit into both keyword and author indexes.

        Args:
            commit: Commit instance to index.
        """
        # [1차]: 커밋 메시지로부터 정규화된 단어 토큰 리스트를 추출합니다.
        # [2차]: 커밋 메모 글에서 핵심 단어들을 쏙쏙 뽑아냅니다.
        tokens = self.tokenize(commit.message)

        # [1차]: 동일한 커밋 내에서 중복 등장한 토큰을 방어하기 위한 집합(Set)입니다.
        # [2차]: 같은 글에서 같은 단어가 여러 번 나와도 한 번만 등록하도록 체크하는 체크리스트입니다.
        seen_tokens: Set[str] = set()

        # [1차]: 추출된 각 단어 토큰을 순회하며 색인에 등록합니다.
        # [2차]: 뽑아낸 단어들을 하나씩 들고 색인 노트를 찾아갑니다.
        for token in tokens:
            # [1차]: 이번 커밋에서 아직 등록하지 않은 단어인지 확인합니다.
            # [2차]: 이미 방금 전에 등록한 단어가 아니라면 작업을 진행합니다.
            if token not in seen_tokens:
                # [1차]: 확인된 토큰을 방문 집합에 기록합니다.
                # [2차]: 방금 본 단어의 체크리스트에 동그라미를 칩니다.
                # 마이: 기존에 없었으면 신규로 등록함
                seen_tokens.add(token)

                # [1차]: 키워드 색인에 해당 단어 키가 없으면 빈 리스트로 초기화합니다.
                # [2차]: 색인 노트에 처음 등장하는 단어라면 새 페이지를 한 장 만듭니다.
                if token not in self._keyword_index:
                    self._keyword_index[token] = []

                # [1차]: 해당 단어의 커밋 해시 리스트 끝에 현재 커밋 해시를 추가합니다.
                # [2차]: 그 단어 페이지 맨 아래에 이번 커밋 번호를 적어 넣습니다.
                # 마이: 키워드에 해쉬 값으로 추ㅏ하는 과정
                self._keyword_index[token].append(commit.hash)

        # [1차]: 작성자 이름 앞뒤 공백을 제거하고 소문자로 정규화합니다.
        # [2차]: 작성자 이름표의 공백을 다듬고 영문 소문자로 통일합니다.
        author_key = commit.author.strip().lower()

        # [1차]: 작성자 색인에 해당 작성자 키가 없으면 빈 리스트로 초기화합니다.
        # [2차]: 처음 보는 작성자라면 작가별 서랍을 새로 하나 만듭니다.
        if author_key not in self._author_index:
            self._author_index[author_key] = []

        # [1차]: 해당 작성자의 커밋 목록에 현재 커밋 해시가 없으면 추가합니다.
        # [2차]: 그 작가의 서랍 속에 이번 커밋 카드를 쏙 집어넣습니다.
        if commit.hash not in self._author_index[author_key]:
            self._author_index[author_key].append(commit.hash)

    # [1차]: 특정 키워드로 역색인을 조회하여 매칭되는 커밋 해시 리스트를 반환하는 메서드입니다.
    # [2차]: 단어 하나를 외치면 그 단어가 적힌 모든 커밋 번호를 0.0001초 만에 찾아주는 번개 검색입니다.
    def search_keyword(self, keyword: str) -> List[str]:
        """Finds all commit hashes associated with a keyword token.

        Time Complexity: O(1) lookup in hash table.

        Args:
            keyword: Word to search.

        Returns:
            List of matching commit hashes (empty list if no match).
        """
        # [1차]: 검색 키워드의 공백을 제거하고 소문자로 정규화합니다.
        # [2차]: 찾고자 하는 단어의 대소문자를 색인 규격에 맞게 소문자로 바꿉니다.
        norm = keyword.strip().lower()

        # [1차]: 딕셔너리 get으로 O(1) 조회 후 리스트 복사본을 반환합니다. 없으면 빈 리스트입니다.
        # [2차]: 색인 책을 단번에 펼쳐 적혀있는 번호들을 복사해 돌려줍니다.
        return list(self._keyword_index.get(norm, []))

    # [1차]: 특정 작성자 이름으로 역색인을 조회하여 매칭되는 커밋 해시 리스트를 반환하는 메서드입니다.
    # [2차]: 작가 이름을 외치면 그 작가가 작성한 모든 커밋 번호를 즉시 찾아주는 전용 검색기입니다.
    def search_author(self, author: str) -> List[str]:
        """Finds all commit hashes associated with an author.

        Time Complexity: O(1) lookup in hash table.

        Args:
            author: Author name to search.

        Returns:
            List of matching commit hashes (empty list if no match).
        """
        # [1차]: 검색할 작성자 이름의 공백을 제거하고 소문자로 정규화합니다.
        # [2차]: 찾고자 하는 작가 명찰을 소문자로 깔끔히 정리합니다.
        norm = author.strip().lower()

        # [1차]: 딕셔너리 get으로 O(1) 조회 후 리스트 복사본을 반환합니다. 없으면 빈 리스트입니다.
        # [2차]: 작가 서랍을 즉시 열어 들어있는 커밋 카드 번호들을 복사해 건네줍니다.
        return list(self._author_index.get(norm, []))
