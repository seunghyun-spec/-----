# 네이버 오픈API 개발 문서 모음 (Naver Open API Documentation)

네이버 개발자 센터(Naver Developers)의 데이터랩(DataLab), 검색(Search) 및 비로그인 방식 오픈 API 관련 공식 문서를 상세히 정리한 개발 문서 모음입니다.

---

## 📚 문서 목차

| 번호 | 문서명 | 파일 링크 | 설명 |
| :---: | :--- | :--- | :--- |
| **01** | **오픈API 종류 및 비로그인 API 개발 가이드** | [01_개발가이드_오픈API_종류_및_비로그인_API.md](./01_개발가이드_오픈API_종류_및_비로그인_API.md) | 로그인/비로그인 API 구분, 전체 API 목록, Client ID/Secret 인증 방식, 애플리케이션 등록 환경 설정 |
| **02** | **데이터랩(DataLab) 서비스 개요** | [02_데이터랩_서비스_소개.md](./02_데이터랩_서비스_소개.md) | 통합검색어 트렌드 및 쇼핑인사이트 서비스 개념, 카테고리 분류 체계, 상대 지표 산출 원리 |
| **03** | **데이터랩 쇼핑인사이트 API 명세서** | [03_데이터랩_쇼핑인사이트_API.md](./03_데이터랩_쇼핑인사이트_API.md) | 쇼핑인사이트 8대 엔드포인트 전체 명세, 파라미터, 요청/응답 스키마, 오류 코드, 5개 언어별 예제 |
| **04** | **데이터랩 통합 검색어 트렌드 API 명세서** | [04_데이터랩_통합검색어트렌드_API.md](./04_데이터랩_통합검색어트렌드_API.md) | 통합검색어 트렌드 API 엔드포인트 명세, 파라미터, 응답 규격, 오류 코드, 5개 언어별 예제 |
| **05** | **검색 API: 쇼핑 검색 명세서** | [05_검색_쇼핑_API.md](./05_검색_쇼핑_API.md) | 네이버 쇼핑 검색 API 명세(XML/JSON), 쿼리 파라미터, 필터/제외 옵션, 상품군 타입, 5개 언어별 예제 |
| **SOP** | **[작업지시서] 일자별 쇼핑트렌드 수집 및 검증** | [작업지시서_일자별_쇼핑트렌드_수집_및_검증.md](./작업지시서_일자별_쇼핑트렌드_수집_및_검증.md) | 최근 1년간 일자별 쇼핑트렌드 데이터 수집, 정제, 4대 무결성 검증, 자동화 스크립트 SOP |

---

## 🔑 비로그인 방식 오픈 API 공통 인증 및 호출 규격

네이버 비로그인 오픈 API는 네이버 로그인 OAuth2 인증(Access Token) 없이, HTTP Header에 발급받은 **클라이언트 아이디**와 **클라이언트 시크릿**을 전송하여 호출합니다.

### 1. HTTP 요청 헤더 (Request Headers)
```http
X-Naver-Client-Id: {애플리케이션 등록 시 발급받은 Client ID}
X-Naver-Client-Secret: {애플리케이션 등록 시 발급받은 Client Secret}
```

### 2. 주요 API별 호출 한도 및 규격 비교

| API 구분 | 엔드포인트 URL | HTTP 메서드 | 데이터 포맷 | 하루 호출 한도 |
| :--- | :--- | :---: | :---: | :---: |
| **쇼핑인사이트 분야별 트렌드** | `https://openapi.naver.com/v1/datalab/shopping/categories` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 분야 내 기기별** | `https://openapi.naver.com/v1/datalab/shopping/category/device` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 분야 내 성별** | `https://openapi.naver.com/v1/datalab/shopping/category/gender` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 분야 내 연령별** | `https://openapi.naver.com/v1/datalab/shopping/category/age` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 키워드별 트렌드** | `https://openapi.naver.com/v1/datalab/shopping/category/keywords` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 키워드 기기별** | `https://openapi.naver.com/v1/datalab/shopping/category/keyword/device` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 키워드 성별** | `https://openapi.naver.com/v1/datalab/shopping/category/keyword/gender` | POST | JSON | 1,000회 / 일 |
| **쇼핑인사이트 키워드 연령별** | `https://openapi.naver.com/v1/datalab/shopping/category/keyword/age` | POST | JSON | 1,000회 / 일 |
| **통합 검색어 트렌드** | `https://openapi.naver.com/v1/datalab/search` | POST | JSON | 1,000회 / 일 |
| **쇼핑 검색 (JSON)** | `https://openapi.naver.com/v1/search/shop.json` | GET | JSON | 25,000회 / 일 |
| **쇼핑 검색 (XML)** | `https://openapi.naver.com/v1/search/shop.xml` | GET | XML | 25,000회 / 일 |

---

## 💄 뷰티 트렌드 분석을 위한 쇼핑인사이트 팁

- **화장품/미용 카테고리 ID**: `50000002`
  - 패션의류: `50000000`
  - 패션잡화: `50000001`
  - 화장품/미용: `50000002`
  - 디지털/가전: `50000003`
  - 출산/육아: `50000005`
  - 식품: `50000006`
  - 스포츠/레저: `50000007`
  - 생활/건강: `50000008`
- **트렌드 지수 해석**:
  - API 결과값의 `ratio`는 조회 기간 내 최대 클릭 횟수를 **100**으로 환산한 **상대적 지표(Index)**입니다.
  - 절대적 클릭 횟수가 아니므로, 특정 시점 대비 검색/클릭 추이 변동 및 키워드/성별/연령별 비중을 분석하는 데 최적화되어 있습니다.
