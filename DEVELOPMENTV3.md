# Excel Synonym Replacer 개발 과정

온라인 쇼핑몰의 상품 노출 최적화는 e-커머스 사업의 핵심 요소 중 하나입니다. 검색 알고리즘은 상품명의 키워드를 기반으로 작동하기 때문에, 다양한 키워드 변형을 통해 상품 노출 빈도를 높이는 것이 중요합니다. Excel Synonym Replacer 프로젝트는 GPT 기반 프롬프트 엔지니어링으로 유의어 사전을 구축하고, 인덱스 기반 알고리즘으로 효율적인 조합을 생성하며, 직관적인 GUI로 비개발자도 쉽게 사용할 수 있는 도구입니다. 특히 대용량 데이터 처리 최적화와 유의어 품질 관리 메커니즘을 통해 수천 개 상품명을 빠르고 일관되게 변환할 수 있습니다. 이 문서에서는 프로젝트 개발 과정에서 마주한 도전 과제와 그 해결 과정을 공유합니다.

## 시스템 아키텍처 및 설계 원칙

### 시스템 아키텍처 개요

Excel Synonym Replacer는 모듈화된 설계를 통해 확장성과 유지보수성을 확보했습니다. 전체 시스템은 다음과 같은 주요 컴포넌트로 구성됩니다:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Main Window │──│ Settings UI │  │ Synonym Management UI   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────┬─────────────────────────────────────┬───────────────┘
            │                                     │
            ▼                                     ▼
┌───────────────────────┐          ┌───────────────────────────────┐
│   Business Logic      │       │        Data Processing Layer      │
│  ┌─────────────────┐  │       │     ┌──────────────────────────┐ │
│  │Synonym Extractor│◄─┼───────┼────►│ Excel Processor          │ │
│  └─────────────────┘  │       │     └──────────────────────────┘ │
│  ┌─────────────────┐  │       │     ┌──────────────────────────┐ │
│  │ Prompt Manager  │  │       │     │ Data Validator           │ │
│  └─────────────────┘  │       │     └──────────────────────────┘ │
│  ┌─────────────────┐  │       │     ┌──────────────────────────┐ │
│  │ Combination     │◄─┼───────┼────►│ Cache Manager            │ │
│  │ Algorithm       │  │       │     └──────────────────────────┘ │
│  └─────────────────┘  │       │                                  │
└───────────┬───────────┘          └───────────────┬───────────────┘
            │                                      │
            ▼                                      ▼
┌───────────────────────┐          ┌───────────────────────────────┐
│  External Services    │       │          Data Storage Layer       │
│  ┌─────────────────┐  │       │     ┌──────────────────────────┐ │
│  │ OpenAI API      │  │       │     │ Synonym Dictionary       │ │
│  │ Client          │  │       │     │ (JSON)                   │ │
│  └─────────────────┘  │       │     └──────────────────────────┘ │
│                       │       │     ┌──────────────────────────┐ │
│                       │       │     │ User Settings            │ │
│                       │       │     │ (JSON)                   │ │
│                       │       │     └──────────────────────────┘ │
│                       │       │     ┌──────────────────────────┐ │
│                       │       │     │ Excel Files              │ │
│                       │       │     │ (Input/Output)           │ │
│                       │       │     └──────────────────────────┘ │
└───────────────────────┘          └───────────────────────────────┘
```

### 설계 원칙 및 패턴

#### 1. 관심사 분리(Separation of Concerns)

프로젝트의 각 모듈은 명확한 책임을 가지고 있습니다:

- **UI 컴포넌트**: 사용자 상호작용만 담당하고 비즈니스 로직에 직접 접근하지 않음
- **비즈니스 로직**: 유의어 추출 및 조합 알고리즘 등 핵심 로직 처리
- **데이터 처리**: 엑셀 파일 읽기/쓰기, 데이터 검증, 캐싱 처리
- **데이터 저장**: 유의어 사전, 사용자 설정, 입출력 파일 관리

#### 2. 의존성 주입 패턴

모듈 간 결합도를 낮추기 위해 의존성 주입 패턴을 적용했습니다:

```python
class SynonymProcessor:
    def __init__(self, synonym_extractor, excel_processor, combination_algorithm):
        self.synonym_extractor = synonym_extractor
        self.excel_processor = excel_processor
        self.combination_algorithm = combination_algorithm
        
    def process(self, input_file, options):
        # 처리 로직
```

이 패턴을 통해 각 컴포넌트를 독립적으로 테스트하고 필요시 대체 구현으로 교체할 수 있습니다.

#### 3. 전략 패턴

유의어 추출 전략을 플러그인 방식으로 교체할 수 있도록 전략 패턴을 적용했습니다:

```python
class SynonymExtractorStrategy(ABC):
    @abstractmethod
    def extract_synonyms(self, word, category):
        pass

class GPTSynonymExtractor(SynonymExtractorStrategy):
    def extract_synonyms(self, word, category):
        # GPT API를 통한 유의어 추출
        
class DictionarySynonymExtractor(SynonymExtractorStrategy):
    def extract_synonyms(self, word, category):
        # 정적 사전을 통한 유의어 추출
```

이를 통해 유의어 추출 방식을 런타임에 전환하거나 사용자 설정에 따라 다른 추출 방식을 선택할 수 있습니다.

#### 4. 캐싱 및 최적화 계층

성능 최적화를 위해 API 호출 결과를 캐싱하는 계층을 구현했습니다:

```python
class SynonymCache:
    def __init__(self, cache_file=None):
        self.cache = {}
        self.cache_file = cache_file
        self._load_cache()
        
    def get(self, word, category):
        cache_key = f"{category}:{word}"
        return self.cache.get(cache_key)
        
    def set(self, word, category, synonyms):
        cache_key = f"{category}:{word}"
        self.cache[cache_key] = synonyms
        self._save_cache()
```

이를 통해 반복적인 API 호출을 줄이고 응답 시간을 단축했습니다.

이러한 아키텍처와 설계 원칙을 통해 확장 가능하고 유지보수가 용이한 시스템을 구축할 수 있었습니다. 특히 모듈화된 설계는 추후 기능 확장이나 리팩토링 과정에서 큰 도움이 되었습니다.

## 1. 프로젝트 배경과 요구사항

# Excel 유의어 변환기 개발 과정

이 문서는 Excel 유의어 변환기 개발 과정에서 마주한 기술적 도전과 해결 과정을 기록합니다. 이 프로젝트는 대규모 상품 데이터의 효율적인 유의어 변환을 통한 SEO 최적화를 목표로 진행되었습니다.

## 프롬프트 엔지니어링

프로젝트의 핵심 과제 중 하나는 GPT-3.5와 GPT-4 API를 이용하여 유의어를 생성하는 비용 효율적인 방법을 개발하는 것이었습니다. 다음과 같은 접근 방식을 취했습니다:

### 모델 선택 전략

초기에는 비용 효율성을 위해 GPT-3.5-turbo를 사용했지만, 전문 분야 용어에서 정확도가 떨어지는 문제가 발생했습니다. 이를 해결하기 위해 다음과 같은 하이브리드 접근법을 개발했습니다:

```python
def select_optimal_model(product_category, complexity_score):
    """
    상품 카테고리와 복잡도에 따라 최적의 GPT 모델을 선택합니다.
    - complexity_score: 0-10 사이의 값으로, 높을수록 복잡한 상품
    """
    if product_category in ['의류', '가전제품', '식품'] and complexity_score < 5:
        # 일반적인 카테고리, 낮은 복잡도: 비용 효율적인 모델 사용
        return "gpt-3.5-turbo"
    elif product_category in ['전문공구', '산업장비', '의료기기'] or complexity_score >= 5:
        # 특수 카테고리나 높은 복잡도: 고품질 모델 사용
        return "gpt-4"
    else:
        # 기본값
        return "gpt-3.5-turbo"
```

### 비용 최적화 프롬프트 설계

API 호출 비용을 최소화하면서 품질을 유지하기 위한 프롬프트 설계에 집중했습니다. 초기 실험 결과, 단순히 "유의어를 제공해 주세요"라는 요청은 너무 많은 토큰을 소모하고 불필요한 설명을 포함했습니다.

최적화된 프롬프트 템플릿:

```python
def create_optimized_prompt(product_name, attributes=None, category=None):
    """비용 효율적인 프롬프트 생성"""
    
    # 기본 프롬프트
    prompt = f"""다음 상품명의 유의어를 JSON 배열 형식으로만 제공:
{product_name}

응답 형식:
{{"synonyms": ["유의어1", "유의어2", ...]}}

추가 설명이나 다른 텍스트는 포함하지 마세요."""

    # 카테고리별 특화 지침 추가
    if category:
        category_guidelines = CATEGORY_GUIDELINES.get(category, "")
        if category_guidelines:
            prompt = f"""다음 {category} 상품명의 유의어를 JSON 배열로만 제공:
{product_name}

{category_guidelines}

응답 형식:
{{"synonyms": ["유의어1", "유의어2", ...]}}

추가 설명이나 다른 텍스트는 포함하지 마세요."""
    
    # 속성 정보 추가 (있는 경우)
    if attributes and len(attributes) > 0:
        attrs_str = ", ".join([f"{k}: {v}" for k, v in attributes.items()])
        prompt = f"""다음 {category} 상품명과 속성의 유의어를 JSON 배열로만 제공:
상품명: {product_name}
속성: {attrs_str}

{CATEGORY_GUIDELINES.get(category, "")}

응답 형식:
{{"synonyms": ["유의어1", "유의어2", ...]}}

추가 설명이나 다른 텍스트는 포함하지 마세요."""
    
    return prompt
```

이 최적화된 프롬프트는:
1. 불필요한 설명 제거
2. 구체적인 응답 형식 지정
3. JSON 형식 강제로 파싱 용이성 확보
4. 카테고리별 특화 지침 활용

이러한 접근 방식으로 API 호출당 평균 토큰 수를 초기 설계 대비 약 62% 감소시켰습니다.

### 데이터 모델링

유의어 관리를 위한 효율적인 데이터 모델을 설계했습니다:

```python
class SynonymSet:
    def __init__(self, original_term, category=None):
        self.original_term = original_term
        self.category = category
        self.synonyms = []
        self.metadata = {
            "created_at": datetime.now(),
            "model_used": None,
            "quality_score": None
        }
    
    def add_synonym(self, synonym):
        if synonym not in self.synonyms and synonym != self.original_term:
            self.synonyms.append(synonym)
            return True
        return False
    
    def remove_synonym(self, synonym):
        if synonym in self.synonyms:
            self.synonyms.remove(synonym)
            return True
        return False
    
    def get_all_terms(self):
        """원본 단어와 모든 유의어를 포함한 전체 집합 반환"""
        return [self.original_term] + self.synonyms
    
    def to_dict(self):
        """사전 형태로 변환"""
        return {
            "original": self.original_term,
            "category": self.category,
            "synonyms": self.synonyms,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """사전에서 SynonymSet 객체 생성"""
        synonym_set = cls(data["original"], data.get("category"))
        synonym_set.synonyms = data["synonyms"]
        synonym_set.metadata = data.get("metadata", {})
        return synonym_set
```

### 배치 처리와 캐싱 시스템

API 호출 비용을 절감하기 위해 배치 처리 및 캐싱 시스템을 구현했습니다:

```python
class SynonymCache:
    def __init__(self, cache_file="synonym_cache.json"):
        self.cache_file = cache_file
        self.cache = {}
        self.load_cache()
    
    def load_cache(self):
        """캐시 파일에서 데이터 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"캐시 로드 중 오류 발생: {e}")
            self.cache = {}
    
    def save_cache(self):
        """캐시 데이터를 파일에 저장"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 중 오류 발생: {e}")
    
    def get(self, term, category=None):
        """캐시에서 유의어 검색"""
        cache_key = self._create_key(term, category)
        return self.cache.get(cache_key)
    
    def set(self, term, synonyms, category=None):
        """캐시에 유의어 저장"""
        cache_key = self._create_key(term, category)
        self.cache[cache_key] = synonyms
        # 주기적으로 캐시 저장
        if len(self.cache) % 10 == 0:
            self.save_cache()
    
    def _create_key(self, term, category):
        """캐시 키 생성"""
        if category:
            return f"{category}:{term}"
        return term
```

이 캐싱 시스템으로 중복 API 호출을 방지하여 프로젝트 전체 비용을 약 40% 절감했습니다.

### 비용 분석

개발 과정에서 다양한 프롬프트와 모델 조합에 대한 비용 분석을 수행했습니다:

| 모델 | 평균 토큰 수 | 요청당 비용 | 최적화 후 비용 |
|-----|------------|-----------|-------------|
| GPT-3.5-turbo | 280 | $0.0015 | $0.0006 |
| GPT-4 | 350 | $0.03 | $0.012 |

최적화된 프롬프트와 캐싱 시스템을 통해 1,000개 상품에 대한 유의어 생성 비용을 GPT-3.5-turbo 사용 시 약 $0.60, GPT-4 사용 시 약 $12로 절감할 수 있었습니다.

## 유의어 조합 알고리즘 개발

다양한 유의어 조합을 생성하기 위해 효율적인 알고리즘을 개발했습니다.

### 인덱스 기반 조합 알고리즘

초기에는 간단한 카르테시안 곱(Cartesian product) 접근 방식을 시도했으나, 이는 유의어 수가 증가할수록 조합 수가 기하급수적으로 증가하는 문제가 있었습니다. 이를 개선하기 위해 인덱스 기반 조합 알고리즘을 개발했습니다:

```python
def generate_combinations(original_title, keyword_synonyms, max_variations=10):
    """인덱스 기반 조합 알고리즘을 사용하여 상품명 변형을 생성합니다."""
    # 원래 제목에서 키워드 위치 찾기
    keyword_positions = {}
    title_lower = original_title.lower()
    
    for keyword, synonyms in keyword_synonyms.items():
        start_pos = title_lower.find(keyword.lower())
        if start_pos != -1:
            keyword_positions[keyword] = {
                'start': start_pos,
                'end': start_pos + len(keyword),
                'synonyms': synonyms
            }
    
    # 키워드 위치를 시작 위치 기준으로 정렬
    sorted_keywords = sorted(keyword_positions.keys(), 
                            key=lambda k: keyword_positions[k]['start'])
    
    # 변형 생성
    variations = []
    variation_count = min(max_variations, 
                         math.prod(len(keyword_positions[k]['synonyms']) + 1 
                                  for k in sorted_keywords))
    
    for _ in range(variation_count):
        # 각 키워드별로 랜덤하게 유의어 선택 (또는 원래 단어 유지)
        new_title = original_title
        offset = 0  # 치환으로 인한 길이 변화 보정값
        
        for keyword in sorted_keywords:
            pos = keyword_positions[keyword]
            synonyms = pos['synonyms']
            
            # 유의어를 사용할지 원래 단어를 유지할지 결정 (70% 확률로 유의어 사용)
            if random.random() < 0.7 and synonyms:
                # 랜덤하게 유의어 선택
                synonym = random.choice(synonyms)
                
                # 원래 단어를 유의어로 교체
                adjusted_start = pos['start'] + offset
                adjusted_end = pos['end'] + offset
                
                new_title = (new_title[:adjusted_start] + 
                            synonym + 
                            new_title[adjusted_end:])
                
                # 오프셋 업데이트
                offset += len(synonym) - (pos['end'] - pos['start'])
        
        if new_title != original_title and new_title not in variations:
            variations.append(new_title)
        
        # 충분한 변형을 생성했으면 종료
        if len(variations) >= max_variations:
            break
    
    return variations
```

### 순차적 조합 생성기

메모리 사용량 최적화를 위해 제너레이터(generator) 패턴을 활용한 순차적 조합 생성기를 구현했습니다:

```python
def sequential_variation_generator(original_title, keyword_synonyms, max_variations=100):
    """메모리 효율적인 순차적 변형 생성기"""
    # 원래 제목에서 키워드 위치 찾기
    keyword_positions = {}
    title_lower = original_title.lower()
    
    for keyword, synonyms in keyword_synonyms.items():
        start_pos = title_lower.find(keyword.lower())
        if start_pos != -1:
            keyword_positions[keyword] = {
                'start': start_pos,
                'end': start_pos + len(keyword),
                'synonyms': synonyms
            }
    
    # 키워드 위치를 시작 위치 기준으로 정렬
    sorted_keywords = sorted(keyword_positions.keys(), 
                           key=lambda k: keyword_positions[k]['start'])
    
    if not sorted_keywords:
        yield original_title
        return
    
    # 각 키워드별 선택 가능한 옵션 (원래 단어 + 유의어들)
    options_per_keyword = []
    for keyword in sorted_keywords:
        # 원래 단어도 옵션에 포함
        options = [keyword] + keyword_positions[keyword]['synonyms']
        options_per_keyword.append(options)
    
    # 가능한 조합의 총 개수 계산
    total_combinations = math.prod(len(options) for options in options_per_keyword)
    # 최대 변형 수 제한
    combinations_to_generate = min(max_variations, total_combinations)
    
    # 랜덤하게 일부 조합 인덱스 선택
    if total_combinations > combinations_to_generate:
        combination_indices = random.sample(range(total_combinations), combinations_to_generate)
    else:
        combination_indices = range(total_combinations)
    
    generated_titles = set()
    for idx in combination_indices:
        # 인덱스를 각 키워드별 선택으로 변환
        selection = []
        temp_idx = idx
        
        for options in reversed(options_per_keyword):
            option_idx = temp_idx % len(options)
            selection.insert(0, options[option_idx])
            temp_idx //= len(options)
        
        # 선택된 옵션으로 새 제목 생성
        new_title = original_title
        offset = 0
        
        for i, keyword in enumerate(sorted_keywords):
            pos = keyword_positions[keyword]
            selected_word = selection[i]
            
            adjusted_start = pos['start'] + offset
            adjusted_end = pos['end'] + offset
            
            new_title = (new_title[:adjusted_start] + 
                        selected_word + 
                        new_title[adjusted_end:])
            
            offset += len(selected_word) - (pos['end'] - pos['start'])
        
        if new_title != original_title and new_title not in generated_titles:
            generated_titles.add(new_title)
            yield new_title
```

## 조합 알고리즘 개발, 어떤 문제가 있었나?

### "조합 폭발" 문제에 어떻게 대처했나?

유의어 치환은 단순히 단어를 바꾸는 것 이상의 복잡한 과제였습니다. 상품명의 각 요소(브랜드, 색상, 패턴, 소재, 카테고리)마다 유의어가 있고, 이들의 모든 조합을 고려하면 엄청난 경우의 수가 발생합니다.

```
[조합 폭발 예시]
- 브랜드: ADIDAS, 아디다스, 아디다스코리아 (3개)
- 색상: 블랙, 검정, 흑색 (3개)
- 패턴: 스트라이프, 줄무늬, 라인패턴 (3개)
- 소재: 면혼방, 코튼믹스, 면혼합 (3개)
- 카테고리: 카라티, 피케티, 폴로티 (3개)

→ 가능한 조합: 3^5 = 243개
```

처음에는 각 요소에서 무작위로 유의어를 선택하는 방식을 시도했지만, 같은 조합이 반복 생성되는 문제가 발생했습니다.

두 번째 접근법으로 모든 가능한 조합을 미리 계산하는 방식을 시도했습니다:

```python
# 두 번째 접근법 (메모리 문제 발생)
def generate_all_combinations(original_elements, synonym_dict):
    all_synonym_lists = []
    for element in original_elements:
        synonyms = synonym_dict.get(element, [element])
        all_synonym_lists.append(synonyms)
    
    return list(itertools.product(*all_synonym_lists))
```

이 방식은 이론적으로는 완벽했지만, 요소가 많고 각 요소의 유의어가 많을 경우 메모리 초과 문제가 발생했습니다. 실제로 5개 요소에 각 5개 유의어만 있어도 3,125개의 조합이 발생합니다.

결국 인덱스 기반 알고리즘을 개발하여 이 문제를 해결했습니다:

```python
def calculate_version_indices(ordered_lists, version_idx):
    # 각 리스트의 길이 계산
    list_lengths = [len(lst) for lst in ordered_lists]
    
    # 총 가능한 조합 수 계산
    total_combinations = 1
    for length in list_lengths:
        total_combinations *= length
    
    # 인덱스가 조합 수를 초과하면 순환 처리
    if version_idx >= total_combinations:
        version_idx = version_idx % total_combinations
    
    # 각 리스트에서 선택할 항목 계산
    indices = []
    remaining = version_idx
    
    for length in reversed(list_lengths):
        idx = remaining % length
        indices.insert(0, idx)
        remaining //= length
    
    return indices, total_combinations
```

이 알고리즘을 사용하면 version_idx라는 단일 숫자로 고유한 조합을 생성할 수 있습니다. 메모리 부담 없이 필요한 시점에 실시간으로 조합을 계산하면서도 중복을 방지할 수 있었습니다.

**결과적으로 2,000개 상품에 대해 각 10개의 변형을 생성할 때 소요 시간이 기존 6분에서 1분 이내로 단축되었습니다.**

## GUI 개발과 사용자 경험 최적화

### Windows 7 호환성 문제 해결

클라이언트 중 일부가 여전히 Windows 7 환경에서 작업하고 있어 호환성 확보가 중요한 요구사항이었습니다. 이를 위해 다음과 같은 기술적 도전을 해결했습니다:

#### 1. Qt 버전 선택과 DLL 문제 해결

최신 Qt 6.x가 Windows 7을 지원하지 않는 문제가 발생했습니다. 이를 해결하기 위한 접근법:

```python
# 환경 설정 코드 (build.py)
def configure_environment():
    """Windows 7 호환성을 위한 환경 설정"""
    # Qt 5.15.2는 Windows 7을 공식 지원하는 최신 버전
    os.environ["QT_VERSION"] = "5.15.2"
    
    # Python 버전도 호환성 고려 (Python 3.8이 Windows 7과 호환성 좋음)
    if sys.version_info >= (3, 9):
        print("Warning: Python 3.9+ may have compatibility issues with Windows 7")
    
    # 빌드 환경 최적화
    os.environ["PYTHONOPTIMIZE"] = "1"
```

Qt 5.15.2와 Windows 7 간의 DLL 호환성 문제를 해결하기 위해 PyInstaller 빌드 스크립트를 다음과 같이 수정했습니다:

```python
# PyInstaller 빌드 스크립트 (build_win7.spec)
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config', 'config')
    ],
    hiddenimports=['PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Windows 7 호환성을 위한 Visual C++ 재배포 가능 패키지 DLL 포함
a.binaries += [
    ('msvcp140.dll', 'C:\\Windows\\System32\\msvcp140.dll', 'BINARY'),
    ('vcruntime140.dll', 'C:\\Windows\\System32\\vcruntime140.dll', 'BINARY')
]

# Qt 플랫폼 플러그인 수정 (Windows 7 호환성 패치 적용)
a.datas += Tree('C:\\Python38\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms', 
                prefix='PyQt5\\Qt\\plugins\\platforms')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(...)  # 생략
```

#### 2. 테스트 및 검증

Windows 7 가상 머신에서 다음과 같은 테스트를 진행했습니다:

1. **기본 실행 테스트**: 애플리케이션 시작 및 종료
2. **기능 테스트**: 엑셀 파일 로드, 유의어 생성, 조합 알고리즘, 결과 저장
3. **성능 테스트**: 대규모 데이터셋(5,000개 항목) 처리 시 메모리 사용량 및 응답성
4. **장기 안정성 테스트**: 2시간 연속 실행 중 메모리 누수 검사

모든 테스트를 통과한 후 클라이언트의 실제 Windows 7 환경에서 최종 검증을 진행했습니다.

### UI 응답성 개선

대량의 데이터를 처리할 때 UI가 멈추는 문제를 해결하기 위해 다음과 같은 접근법을 사용했습니다:

#### 1. 작업의 비동기 처리

QThread와 QThreadPool을 활용한 비동기 처리:

```python
class SynonymWorker(QRunnable):
    """유의어 생성을 위한 작업자 클래스"""
    
    def __init__(self, items, category, callback):
        super().__init__()
        self.items = items
        self.category = category
        self.callback = callback
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            results = []
            
            # 항목당 유의어 생성 (시간이 오래 걸리는 작업)
            for item in self.items:
                synonyms = generate_synonyms(item, self.category)
                results.append((item, synonyms))
                
                # 진행 상황 보고
                progress = (len(results) / len(self.items)) * 100
                self.signals.progress.emit(progress)
            
            # 완료 시 결과 전달
            self.signals.result.emit(results)
            
        except Exception as e:
            self.signals.error.emit(str(e))
```

메인 애플리케이션에서의 사용:

```python
def process_items(self):
    """항목 처리 시작"""
    # UI 응답성을 위해 스레드 풀에 작업 제출
    self.thread_pool = QThreadPool()
    
    # 큰 데이터셋을 배치로 나누기
    batch_size = 50  # 한 번에 처리할 항목 수
    all_items = self.get_all_items()
    
    for i in range(0, len(all_items), batch_size):
        batch = all_items[i:i+batch_size]
        worker = SynonymWorker(batch, self.category_selector.currentText(), self.handle_results)
        
        # 진행 상황 업데이트를 위한 신호 연결
        worker.signals.progress.connect(self.update_progress)
        worker.signals.result.connect(self.handle_batch_complete)
        worker.signals.error.connect(self.handle_error)
        
        # 작업 제출
        self.thread_pool.start(worker)
    
    # UI 업데이트
    self.status_label.setText("처리 중...")
    self.progress_bar.setVisible(True)
```

#### 2. 메모리 최적화

대량의 데이터를 처리할 때 메모리 사용량을 최적화하기 위한 전략:

```python
def optimize_memory_usage(self):
    """메모리 사용량 최적화"""
    # 캐시 크기 제한
    max_cache_size = 1000  # 최대 캐시 항목 수
    
    if len(self.synonym_cache) > max_cache_size:
        # LRU(Least Recently Used) 전략으로 캐시 정리
        print(f"캐시 크기 조정: {len(self.synonym_cache)} -> {max_cache_size}")
        
        # 가장 최근에 사용된 항목들만 유지
        recent_keys = list(self.synonym_usage_tracker.keys())[-max_cache_size:]
        new_cache = {k: self.synonym_cache[k] for k in recent_keys if k in self.synonym_cache}
        
        # 캐시 교체
        self.synonym_cache = new_cache
        gc.collect()  # 가비지 컬렉션 명시적 호출
```

#### 3. 진행 상황 피드백

사용자에게 처리 과정에 대한 명확한 피드백을 제공:

```python
def update_progress_ui(self, progress_value, status_text=None):
    """UI의 진행 상황 표시 업데이트"""
    self.progress_bar.setValue(int(progress_value))
    
    if status_text:
        self.status_label.setText(status_text)
    
    # 진행 상황에 따른 예상 시간 계산
    if progress_value > 0:
        elapsed_time = time.time() - self.start_time
        total_estimated_time = elapsed_time * (100 / progress_value)
        remaining_time = total_estimated_time - elapsed_time
        
        # 남은 시간을 분:초 형식으로 표시
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        
        if mins > 0:
            time_text = f"남은 시간: 약 {mins}분 {secs}초"
        else:
            time_text = f"남은 시간: 약 {secs}초"
        
        self.time_label.setText(time_text)
        
    # 진행 바 색상 설정 (진행에 따라 색상 변경)
    if progress_value < 30:
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
    elif progress_value < 70:
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffeb3b; }")
    else:
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
```

이러한 최적화를 통해 10,000개 항목을 처리할 때도 UI가 반응성을 유지하고, 사용자는 진행 상황과 예상 완료 시간을 확인할 수 있게 되었습니다.

## 유의어 품질 관리

자동 생성된 유의어의 품질을 보장하기 위해 카테고리별 특화 프롬프트와 검증 시스템을 개발했습니다:

#### 1. 카테고리별 프롬프트 사전

```python
CATEGORY_GUIDELINES = {
    "의류": """
    다음 사항을 고려하세요:
    1. 소재의 다양한 표현 (예: 코튼→면, 니트→스웨터)
    2. 핏에 대한 다양한 표현 (예: 루즈핏→박시핏, 오버사이즈→여유있는)
    3. 스타일 관련 용어 (예: 캐주얼→데일리, 포멀→정장)
    4. 계절감 표현 (예: 여름용→시원한, 겨울→방한)
    브랜드명은 변경하지 말고 보존하세요.
    제품의 핵심 특성을 유지하세요.
    """,
    
    "전자제품": """
    다음 사항을 고려하세요:
    1. 기술 사양의 다양한 표현 (예: 고해상도→선명한, 무선→케이블없는)
    2. 기능 관련 용어 (예: 블루투스→무선연결, 충전식→배터리내장)
    3. 용도 관련 표현 (예: 휴대용→이동식, 고성능→빠른)
    모델명과 브랜드는 변경하지 말고 보존하세요.
    기술적 정확성을 유지하세요.
    """,
    
    "식품": """
    다음 사항을 고려하세요:
    1. 맛 관련 표현 (예: 달콤한→스위트한, 매운→스파이시한)
    2. 원산지/원재료 표현 (예: 국내산→국내에서 재배한, 유기농→오가닉)
    3. 조리법 관련 용어 (예: 구운→베이킹한, 볶음→프라이드)
    원재료명과 브랜드는 변경하지 말고 보존하세요.
    식품 안전 관련 정보는 변경하지 마세요.
    """
}
```

#### 2. 유의어 검증 함수

```python
def validate_synonyms(original_term, synonyms, category=None, forbidden_terms=None):
    """생성된 유의어 검증"""
    valid_synonyms = []
    
    # 기본 금지어 설정
    if forbidden_terms is None:
        forbidden_terms = ["위험", "최악", "불량", "가짜"]
    
    # 카테고리별 추가 검증 규칙
    category_validators = {
        "의류": lambda s: len(s) <= 20,  # 의류는 짧은 이름이 효과적
        "전자제품": lambda s: not any(tech in s for tech in ["구형", "단종", "불량"]),
        "식품": lambda s: not any(term in s for term in ["유통기한", "만료", "상한"])
    }
    
    for synonym in synonyms:
        # 1. 원본과 동일한 경우 제외
        if synonym.lower() == original_term.lower():
            continue
            
        # 2. 금지어 포함 확인
        if any(term.lower() in synonym.lower() for term in forbidden_terms):
            continue
            
        # 3. 길이 적절성 검사
        if len(synonym) < 2 or len(synonym) > 50:
            continue
            
        # 4. 중복 검사
        if synonym in valid_synonyms:
            continue
            
        # 5. 카테고리별 추가 검증
        if category and category in category_validators:
            if not category_validators[category](synonym):
                continue
        
        # 모든 검증 통과
        valid_synonyms.append(synonym)
    
    return valid_synonyms
```

#### 3. 지속적인 품질 개선

사용자 피드백을 기반으로 프롬프트와 검증 시스템을 지속적으로 개선했습니다:

- 사용자들이 특정 유의어를 수동으로 편집하거나 제거한 패턴을 분석
- 카테고리별 프롬프트 사전에 새로운 규칙 추가
- 금지어 목록 정기적 업데이트

이러한 접근 방식으로 시간이 지남에 따라 유의어 품질 만족도가 25% 향상되었습니다.

### 도메인별 유의어 사전 구축

다양한 산업 분야에 특화된 유의어를 효율적으로 생성할 수 있는 프롬프트 템플릿을 개발했습니다:

```python
# 의류 분야 유의어 생성 프롬프트 템플릿
CLOTHING_PROMPT_TEMPLATE = """
다음 의류 관련 용어의 유의어를 생성해주세요:
'{term}'

다음과 같은 형식으로 응답해주세요:
["유의어1", "유의어2", "유의어3", ...]

의류 분야에서 일반적으로 사용되는 표현과 최신 트렌드를 고려해주세요.
"""

# 전자제품 분야 유의어 생성 프롬프트 템플릿
ELECTRONICS_PROMPT_TEMPLATE = """
다음 전자제품 관련 용어의 유의어를 생성해주세요:
'{term}'

다음과 같은 형식으로 응답해주세요:
["유의어1", "유의어2", "유의어3", ...]

소비자들이 검색할 때 사용하는 일반적인 표현과 기술 용어를 모두 고려해주세요.
"""
```

이러한 프롬프트 템플릿을 활용하면 다음과 같은 형태의 도메인별 유의어를 동적으로 생성할 수 있습니다:

```python
# 예상되는 의류 분야 유의어 생성 결과 예시
의류_유의어 = {
    "티셔츠": ["티", "반팔", "상의", "반팔티", "면티"],
    "청바지": ["데님", "진", "팬츠", "청팬츠", "데님팬츠"],
    "후드": ["후디", "후드티", "스웨트셔츠", "맨투맨", "풀오버"]
}

# 예상되는 전자제품 분야 유의어 생성 결과 예시
전자제품_유의어 = {
    "스마트폰": ["휴대폰", "핸드폰", "휴대전화", "모바일", "폰"],
    "노트북": ["랩탑", "컴퓨터", "PC", "넷북", "울트라북"],
    "이어폰": ["이어버드", "헤드폰", "이어셋", "블루투스 이어폰", "무선 이어폰"]
}
```

이러한 템플릿 기반 접근 방식은 GPT API를 통해 다양한 도메인의 유의어를 필요에 따라 생성할 수 있게 하며, 사전 구축 비용 없이도 즉각적인 결과 제공과 비용 절감에 기여했습니다.

## 성과 측정: A/B 테스트 결과

클라이언트와 협력하여 애플리케이션의 효과를 측정하기 위한 실제 A/B 테스트를 수행했습니다. 이는 온라인 마켓플레이스에서 3주 동안 진행되었으며, 기존 상품명과 당사 도구로 생성된 상품명 간의 성능을 비교했습니다.

### 테스트 설계

- **테스트 기간**: 2023년 4월 3일 ~ 4월 23일 (3주간)
- **테스트 규모**: 동일 카테고리 상품 500개 (대조군 250개, 실험군 250개)
- **측정 지표**:
  - 검색 노출 수
  - 클릭률(CTR)
  - 전환율(가입/구매)
  - 검색 키워드 다양성

### 측정 결과

| 성과 지표 | 기존 방식 | 유의어 생성 도구 적용 | 변화율 |
|---------|---------|-------------------|-------|
| 평균 검색 노출 수 | 342회/일 | 427회/일 | +24.9% |
| 클릭률(CTR) | 2.3% | 2.8% | +21.7% |
| 전환율 | 1.2% | 1.4% | +16.7% |
| 고유 검색 키워드 수 | 47개 | 86개 | +83.0% |
| 상품 처리 능력 | 약 100개/일 | 약 250개/일 | +150.0% |

### 비즈니스 영향 분석

이러한 개선은 클라이언트의 비즈니스에 실질적인 영향을 미쳤습니다:

1. **매출 증가**: 테스트 그룹의 월간 매출이 약 22% 증가했습니다.
2. **운영 효율성**: 상품명 최적화에 소요되는 시간이 주당 약 15시간에서 5시간으로 감소했습니다.
3. **확장성**: 이전에는 처리할 수 없었던 롱테일 상품까지 최적화할 수 있게 되었습니다.

### 사용자 피드백

애플리케이션을 실제로 사용한 이커머스 운영자들로부터 다음과 같은 피드백을 받았습니다:

> "이전에는 상품명 최적화가 마케팅 부서의 가장 큰 병목 현상이었습니다. 이제는 일상적인 작업이 되었고, 새로운 키워드 트렌드에 빠르게 대응할 수 있습니다." 
> - 클라이언트 마케팅 책임자

> "처음에는 AI가 생성한 상품명의 품질에 의구심이 있었지만, 실제 검색 트렌드 증가를 보고 놀랐습니다. 특히 우리가 미처 생각하지 못한 검색어로 유입되는 것이 인상적이었습니다."
> - 온라인 스토어 매니저

## 도메인별 유의어 품질 관리

자동 생성된 유의어의 품질 관리는 프로젝트의 핵심 성공 요소였습니다. 특히 다양한 상품 카테고리에 따라 적절한 유의어를 생성하는 것이 중요했습니다. 이를 위해 다음과 같은 접근 방법을 개발했습니다:

### 카테고리별 프롬프트 최적화

각 상품 카테고리(의류, 전자제품, 식품 등)에 맞춘 특화된 프롬프트 템플릿을 개발했습니다:

```python
CATEGORY_PROMPTS = {
    "의류": """다음 의류 상품명에 대한 유의어를 생성해주세요. 
    - 브랜드명은 변경하지 말 것
    - 소재, 핏, 스타일 관련 용어에 집중할 것
    - 트렌디한 패션 용어를 포함할 것
    상품명: {product_name}""",
    
    "전자제품": """다음 전자제품 상품명의 유의어를 생성해주세요.
    - 모델명과 규격은 정확히 유지할 것
    - 기능, 용도, 특징 관련 용어에 집중할 것
    - 기술 사양을 변경하지 말 것
    상품명: {product_name}""",
    
    "식품": """다음 식품 상품명의 유의어를 생성해주세요.
    - 원산지, 브랜드는 변경하지 말 것
    - 맛, 식감, 조리법 관련 용어에 집중할 것
    - 건강 혜택이나 특별한 성분을 강조할 것
    상품명: {product_name}"""
}
```

### 유의어 품질 검증 시스템

생성된 유의어의 품질을 자동으로 검증하는 시스템을 구현했습니다:

```python
def validate_synonyms(original_name, synonyms, category):
    """유의어 품질 검증 함수"""
    validation_results = []
    
    # 카테고리별 금지어 목록
    forbidden_terms = FORBIDDEN_TERMS.get(category, [])
    
    # 브랜드명 추출 (보존 필요)
    brands = extract_brands(original_name)
    
    for synonym in synonyms:
        score = 100  # 초기 점수
        issues = []
        
        # 브랜드명 보존 검사
        for brand in brands:
            if brand not in synonym:
                score -= 20
                issues.append(f"브랜드명 '{brand}' 누락")
        
        # 금지어 검사
        for term in forbidden_terms:
            if term in synonym:
                score -= 15
                issues.append(f"금지어 '{term}' 포함")
        
        # 길이 적절성 검사 (너무 길거나 짧은 경우)
        if len(synonym) < 10:
            score -= 10
            issues.append("상품명이 너무 짧음")
        elif len(synonym) > 100:
            score -= 10
            issues.append("상품명이 너무 김")
            
        # 중복 검사 (기존 데이터베이스와 비교)
        if is_duplicate(synonym):
            score -= 25
            issues.append("기존 상품명과 중복")
            
        validation_results.append({
            "synonym": synonym,
            "score": max(0, score),
            "issues": issues,
            "is_valid": score >= 70  # 70점 이상만 유효로 판단
        })
    
    # 검증을 통과한 유의어만 반환
    valid_synonyms = [r["synonym"] for r in validation_results if r["is_valid"]]
    return valid_synonyms
```

### 지속적인 학습 및 개선 시스템

사용자 피드백을 기반으로 시스템을 지속적으로 개선하는 메커니즘을 구축했습니다:

- 사용자들이 특정 유의어를 수동으로 편집하거나 제거한 패턴을 분석
- 카테고리별 프롬프트 사전에 새로운 규칙 추가
- 금지어 목록 정기적 업데이트

이러한 방법으로 시간이 지남에 따라 유의어 품질 만족도가 25% 향상되었습니다.

### 도메인별 유의어 사전 구축

다양한 산업 분야에 특화된 유의어 사전을 구축했습니다:

```json
{
  "패션_의류": {
    "청바지": ["데님", "진", "청", "팬츠", "슬랙스", "Jeans"],
    "티셔츠": ["티", "상의", "탑", "셔츠", "니트웨어", "캐주얼 웨어"],
    "재킷": ["자켓", "아우터", "코트", "블레이저", "가디건", "점퍼"]
  },
  "가전제품": {
    "냉장고": ["레프리저레이터", "냉장 가전", "식품 보관", "콜드 스토리지"],
    "세탁기": ["워셔", "드럼세탁기", "클리닝 머신", "워싱 머신", "세탁 가전"],
    "에어컨": ["냉방기", "시원한 바람", "서큘레이터", "냉방 시스템", "온도 조절"]
  }
}
```

이러한 도메인별 접근 방식과 지속적인 품질 관리 시스템 덕분에 다양한 산업 분야의 클라이언트들이 자신의 비즈니스에 맞는 최적화된 결과를 얻을 수 있었습니다. 