# 네이버 오픈API 개발 가이드: 오픈API 종류 및 비로그인 방식 API

> **출처**: [네이버 개발자 센터 - 오픈API 가이드](https://developers.naver.com/docs/common/openapiguide/apilist.md#비로그인-방식-오픈-api)

---

# 네이버 오픈API 종류

네이버 오픈API는 인증 여부에 따라 로그인 방식 오픈 API와 비로그인 방식 오픈 API로 구분됩니다.

## 로그인 방식 오픈 API

로그인 방식 오픈 API는 '[네이버 로그인](https://developers.naver.com/products/login/api/api.md)'의 인증을 받아 접근 토큰(access token)을 획득해야 사용할 수 있는 오픈 API입니다. API를 호출할 때 네이버 로그인 API를 통해 받은 접근 토큰의 값을 전송해야 합니다.

다음과 같은 네이버 오픈API가 로그인 방식 오픈 API입니다. 회원 기본 정보 조회, 카페 가입 및 글쓰기, 캘린더 일정 담기 등의 기능을 구현할 때 로그인 방식 오픈 API를 사용합니다.

- [네이버 로그인](https://developers.naver.com/products/login/api/api.md): 별도의 아이디와 비밀번호 없이 네이버 아이디로 간편하게 외부 서비스에 로그인할 수 있게 하는 API입니다.
- [카페](https://developers.naver.com/products/login/cafe/cafe.md): 외부 서비스에서 네이버 카페에 가입하거나 게시글을 등록할 수 있게 하는 API입니다.
- [캘린더](https://developers.naver.com/products/login/calendar/calendar.md): 외부 서비스에 네이버 캘린더에 일정을 등록할 수 있게 하는 API입니다.

### 네이버 로그인

다음은 네이버 로그인 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://nid.naver.com/oauth2.0/authorize` | GET/POST | - | 네이버 로그인 인증을 요청합니다. |
| `https://nid.naver.com/oauth2.0/token` | GET/POST | JSON | 접근 토큰의 발급, 갱신, 삭제를 요청합니다. |
| `https://openapi.naver.com/v1/nid/me` | GET | JSON | 네이버 회원의 프로필을 조회합니다. |

### 카페

다음은 카페 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/v1/cafe/{clubid}/members` | POST | JSON | 특정 네이버 카페에 가입합니다. |
| `https://openapi.naver.com/v1/cafe/{clubid}/menu/{menuid}/articles` | POST | JSON | 네이버 카페 게시판에 게시글을 등록합니다. |

### 캘린더

다음은 캘린더 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/calendar/createSchedule.json` | POST | JSON | 네이버 캘린더에 일정을 추가합니다. |

## 비로그인 방식 오픈 API

비로그인 방식 오픈 API는 HTTP 헤더에 클라이언트 아이디와 클라이언트 시크릿 값만 전송해 사용할 수 있는 오픈 API입니다. 네이버 로그인의 인증을 통한 접근 토큰을 획득할 필요가 없습니다.

다음과 같은 네이버 오픈API가 비로그인 방식 오픈 API입니다.

- [데이터랩](https://developers.naver.com/docs/serviceapi/datalab/search/search.md): [네이버 데이터랩](https://datalab.naver.com/)의 [검색어 트렌드](https://datalab.naver.com/keyword/trendSearch.naver)와 [쇼핑인사이트](https://datalab.naver.com/shoppingInsight/sCategory.naver)를 API로 실행할 수 있게 하는 API입니다.
- [검색](https://developers.naver.com/docs/serviceapi/search/blog/blog.md): 네이버 검색 결과를 뉴스, 백과사전, 블로그, 쇼핑, 웹 문서, 전문정보, 지식iN, 책, 카페글 등 분야별로 볼 수 있는 API입니다. 그 외에 지역 검색 결과와 성인 검색어 판별 기능, 오타 변환 기능을 제공합니다.
- [이미지 캡차](https://developers.naver.com/docs/utils/captcha/overview/): 네이버 서비스에서 사용하는 이미지 캡차 기능을 외부 서비스에 사용할 수 있게 하는 API입니다.
- [음성 캡차](https://developers.naver.com/docs/utils/scaptcha/overview/): 네이버 서비스에서 사용하는 음성 캡차 기능을 외부 서비스에 사용할 수 있게 하는 API입니다.
- [네이버 공유하기](https://developers.naver.com/docs/share/navershare/): 콘텐츠를 네이버 블로그, 네이버 카페, PHOLAR에 공유할 수 있게 하는 API입니다.
- [네이버 오픈메인](https://developers.naver.com/docs/openmain/): 웹 페이지를 네이버 메인에 추가할 수 있게 하는 플러그인입니다.

### 데이터랩

다음은 데이터랩 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/v1/datalab/search` | POST | JSON | 그룹으로 묶은 검색어에 대한 네이버 통합검색에서 검색 추이 데이터를 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/categories` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서의 검색 클릭 추이를 쇼핑 분야별로 조회한 데이터를 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/device` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야의 검색 클릭 추이를 기기별(PC, 모바일)로 조회한 데이터를 JSON 형식으로 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/gender` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야의 검색 클릭 추이를 사용자의 성별로 조회한 데이터를 JSON 형식으로 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/age` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야의 검색 클릭 추이를 사용자의 연령별로 조회한 데이터를 JSON 형식으로 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/keywords` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야의 검색 클릭 추이를 검색 키워드별로 조회한 데이터를 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/keyword/device` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야와 검색 키워드의 검색 클릭 추이를 기기별(PC, 모바일)로 조회한 데이터를 JSON 형식으로 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/keyword/gender` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야와 검색 키워드의 검색 클릭 추이를 사용자의 성별로 조회한 데이터를 JSON 형식으로 반환합니다. |
| `https://openapi.naver.com/v1/datalab/shopping/category/keyword/age` | POST | JSON | 네이버 통합검색의 쇼핑 영역과 [네이버쇼핑](https://shopping.naver.com/)에서 특정 쇼핑 분야와 검색 키워드의 검색 클릭 추이를 사용자의 연령별로 조회한 데이터를 JSON 형식으로 반환합니다. |

### 검색

다음은 검색 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/v1/search/news` | GET | JSON, XML | 네이버 검색의 뉴스 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/encyc` | GET | JSON, XML | 네이버 검색의 백과사전 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/blog` | GET | JSON, XML | 네이버 검색의 블로그 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/shop` | GET | JSON, XML | 네이버 검색의 쇼핑 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/webkr` | GET | JSON, XML | 네이버 검색의 웹 문서 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/image` | GET | JSON, XML | 네이버 검색의 이미지 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/doc` | GET | JSON, XML | 네이버 검색의 전문정보 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/kin` | GET | JSON, XML | 네이버 검색의 지식iN 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/book` | GET | JSON, XML | 네이버 검색의 책 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/cafearticle` | GET | JSON, XML | 네이버 검색의 카페글 검색 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/adult` | GET | JSON, XML | 입력한 검색어가 성인 검색어인지 판별한 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/errata` | GET | JSON, XML | 입력한 검색어의 한영 오류를 변환한 결과를 반환합니다. |
| `https://openapi.naver.com/v1/search/local` | GET | JSON, XML | 네이버 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다. |

### 이미지 캡차

다음은 이미지 캡차 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/v1/captcha/ncaptcha.bin` | GET | JPG | 캡차 이미지를 요청합니다. |
| `https://openapi.naver.com/v1/captcha/nkey` | GET | JSON | 캡차 키를 발급하거나 입력값을 비교한 결과를 반환합니다. |

### 음성 캡차

다음은 음성 캡차 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `https://openapi.naver.com/v1/captcha/scaptcha` | GET | WAV | 캡차 음성을 요청합니다. |
| `https://openapi.naver.com/v1/captcha/skey` | GET | JSON | 캡차 키를 발급하거나 입력값을 비교한 결과를 반환합니다. |

### 네이버 공유하기

다음은 네이버 공유하기 API에서 사용하는 주요 요청 URL과 메서드, 응답 형식입니다.

| 요청 URL | 메서드 | 응답 형식 | 설명 |
| --- | --- | --- | --- |
| `http://share.naver.com/web/shareView` | GET | - | 콘텐츠를 네이버 블로그, 네이버 카페, PHOLAR에 공유합니다. |

---

# 부록: 오픈API 애플리케이션 등록 및 환경 설정 가이드

> **출처**: [네이버 개발자 센터 - 애플리케이션 등록 가이드](https://developers.naver.com/docs/common/openapiguide/appregister.md)

# 사전 준비 사항

네이버 오픈API를 사용하려면 먼저 [네이버 개발자 센터](https://developers.naver.com/)에서 애플리케이션을 등록하고 클라이언트 아이디와 클라이언트 시크릿을 발급받아야 합니다.

클라이언트 아이디와 클라이언트 시크릿은 인증된 사용자인지를 확인하는 수단이며, 애플리케이션이 등록되면 발급됩니다. 클라이언트 아이디와 클라이언트 시크릿을 네이버 오픈API를 호출할 때 HTTP 헤더에 포함해서 전송해야 API를 호출할 수 있습니다. API 사용량은 클라이언트 아이디별로 합산됩니다.

> **주의**
> 
> 네이버에 로그인한 사용자 계정으로 애플리케이션이 등록됩니다. 애플리케이션을 등록한 네이버 아이디는 '관리자' 권한을 가지게 되므로 네이버 계정의 보안에 각별히 주의해야 합니다.
> 
> 회사나 단체에서 애플리케이션을 등록할 때는 추후 키 관리 등이 용이하도록 네이버 단체 회원으로 로그인해 이용할 것을 권장합니다.
> 
> 
> 
> [네이버 단체 회원 가입하기](https://nid.naver.com/group/commonAction.nhn?m=viewTerms)

## 애플리케이션 등록

네이버 개발자 센터에서 애플리케이션을 등록하는 방법은 다음과 같습니다.

1. 네이버 개발자 센터의 메뉴에서 **[Application > 애플리케이션 등록](https://developers.naver.com/apps/#/wizard/register)**을 선택합니다.
2. **이용약관 동의** 단계에서 **이용약관에 동의합니다.**를 선택한 다음 **확인**을 클릭합니다.
3. **계정 정보 등록** 단계에서 휴대폰 인증을 완료하고 회사 이름을 입력한 다음 **확인**을 클릭합니다. 휴대폰 인증은 담당자 연락처 확인을 위해 필요한 과정이며, 애플리케이션을 처음 등록할 때 한 번만 인증받으면 됩니다.
4. **애플리케이션 등록 (API이용신청)** 페이지에서 [애플리케이션 등록 세부 정보](https://developers.naver.com/docs/common/openapiguide/appregister.md#%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98-%EB%93%B1%EB%A1%9D-%EC%84%B8%EB%B6%80-%EC%A0%95%EB%B3%B4)를 입력한 다음 **등록하기**를 클릭합니다.

## 애플리케이션 등록 세부 정보

**애플리케이션 등록 (API이용신청)** 페이지에서 애플리케이션 세부 정보를 입력하는 방법은 다음과 같습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-1.png)

1. 등록하려는 애플리케이션의 이름을 **애플리케이션 이름**에 입력합니다.
2. **사용 API**에서 애플리케이션에 사용할 네이버 오픈API를 선택해 추가합니다. API는 여러 개를 추가할 수 있습니다.
3. **로그인 오픈 API 서비스 환경**과 **비로그인 오픈 API 서비스 환경**에서 애플리케이션을 서비스할 환경을 추가하고 필요한 상세 정보를 입력합니다. **로그인 오픈 API 서비스 환경**은 **사용 API**에서 [로그인 방식 오픈 API](https://developers.naver.com/docs/common/openapiguide/apilist.md#%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EB%B0%A9%EC%8B%9D-%EC%98%A4%ED%94%88-api)에 해당하는 API를 선택하면 나타납니다. **비로그인 오픈 API 서비스 환경**은 **사용 API**에서 [비로그인 방식 오픈 API](https://developers.naver.com/docs/common/openapiguide/apilist.md#%EB%B9%84%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EB%B0%A9%EC%8B%9D-%EC%98%A4%ED%94%88-api)에 해당하는 API를 선택하면 나타납니다.

### 애플리케이션 이름

등록할 애플리케이션의 이름을 **애플리케이션 이름**에 입력합니다. 애플리케이션 이름은 최대 40자까지 입력할 수 있습니다.

로그인 방식 오픈 API를 사용할 때는 다음 화면처럼 네이버 로그인 화면에 애플리케이션 이름이 표시되므로 10자 이내의 간결한 이름을 사용하는 것을 권장합니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-2.png)

### 사용 API

애플리케이션에 사용할 네이버 오픈API를 **사용 API**에서 선택해 추가합니다. 여러 개를 추가할 수 있으며, **X**를 클릭하면 API를 목록에서 삭제할 수 있습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-3.png)

> **네이버 로그인**
> 
> 로그인 방식 오픈 API에 해당하는 API인 카페, 캘린더를 선택해 추가하면 **네이버 로그인**이 자동으로 추가됩니다.

### 로그인 오픈 API 서비스 환경

로그인 방식 오픈 API 사용에 필요한 서비스 환경별 상세 정보는 **로그인 오픈 API 서비스 환경**에서 입력합니다.

**환경 추가**에서 애플리케이션을 서비스할 환경을 클릭해 서비스 환경을 추가합니다. 여러 개를 추가할 수 있으며, **X**를 클릭하면 서비스 환경을 목록에서 삭제할 수 있습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-4.png)

서비스 환경에 따라 입력해야 하는 정보는 다음과 같습니다.

#### 안드로이드

- 다운로드 URL: 애플리케이션을 다운로드할 수 있는 Google Play의 URL을 입력합니다. 애플리케이션이 Google Play에 등록되지 않은 상태라면 임의의 URL(예: 개발사 홈페이지 URL)을 입력하고 애플리케이션이 등록된 이후에 변경하십시오.
- 안드로이드 앱 패키지 이름: Android 애플리케이션의 패키지 이름을 입력합니다. 등록된 패키지 이름과 로그인을 시도하는 Android 애플리케이션의 패키지 이름이 다르면 인증에 실패할 수 있습니다.

#### iOS

- 다운로드 URL: 애플리케이션을 다운로드할 수 있는 App Store의 URL을 입력합니다. 애플리케이션이 App Store에 등록되지 않은 상태라면 임의의 URL(예: 개발사 홈페이지 URL)을 입력하고 애플리케이션이 등록된 이후에 변경하십시오.
- URL Scheme: 네이버 앱에서 수행한 로그인 인증 결과를 전달받을 URL Scheme을 입력합니다.

#### Mobile 웹

- 서비스 URL: 모바일 환경에서 웹 서비스에 접속할 URL을 입력합니다. 포트 번호와 프로토콜은 구분하지 않으므로 도메인 이름만 주의해서 입력하세요. `www`를 제외한 도메인을 입력하면 서브 도메인을 따로 입력할 필요가 없습니다. 예를 들어 `naver.com`을 입력하면 `map.naver.com`와 `dev.naver.com` 같은 서브도메인은 입력할 필요가 없습니다.
- 네이버 로그인 Callback URL: 모바일 환경에서 네이버 로그인 인증이 완료되면 인증 성공 여부, 인증 코드 등을 반환할 콜백 URL을 입력합니다. 최대 5개까지 추가할 수 있습니다.

#### PC 웹

- 서비스 URL: 웹 서비스에 접속할 URL을 입력합니다. 포트 번호와 프로토콜은 구분하지 않으므로 도메인 이름만 주의해서 입력하세요. `www`를 제외한 도메인을 입력하면 서브 도메인을 따로 입력할 필요가 없습니다. 예를 들어 `naver.com`을 입력하면 `map.naver.com`와 `dev.naver.com` 같은 서브도메인은 입력할 필요가 없습니다
- 네이버 로그인 Callback URL: 네이버 로그인 인증이 완료되면 인증 성공 여부, 인증 코드 등을 반환할 콜백 URL을 입력합니다. 최대 5개까지 추가할 수 있습니다.

#### Windows App

- 다운로드 URL: 애플리케이션을 다운로드할 수 있는 URL을 입력합니다.
- Callback URL: 네이버 로그인 인증이 완료되면 인증 성공 여부, 인증 코드 등을 반환할 콜백 URL을 입력합니다.

### 비로그인 오픈 API 서비스 환경

비로그인 방식 오픈 API 사용에 필요한 서비스 환경별 상세 정보는 **비로그인 오픈 API 서비스 환경**에서 입력합니다.

**환경 추가**에서 애플리케이션을 서비스할 환경을 클릭해 서비스 환경을 추가합니다. 여러 개를 추가할 수 있으며, **X**를 클릭하면 서비스 환경을 목록에서 삭제할 수 있습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-5.png)

서비스 환경에 따라 입력해야 하는 정보는 다음과 같습니다.

#### Android 설정

- 안드로이드 앱 패키지 이름: Android 애플리케이션의 패키지 이름을 입력합니다.

#### iOS 설정

- iOS Bundle ID: iOS 애플리케이션의 번들 아이디를 입력합니다.

#### WEB 설정

- 웹 서비스 URL: 웹 서비스에 접속할 URL을 입력합니다. 최대 10개까지 추가할 수 있습니다. 포트 번호와 프로토콜은 구분하지 않으므로 도메인 이름만 주의해서 입력하세요. `www`를 제외한 도메인을 입력하면 서브 도메인을 따로 입력할 필요가 없습니다. 예를 들어 `naver.com`을 입력하면 `map.naver.com`와 `dev.naver.com` 같은 서브도메인은 입력할 필요가 없습니다.

## 애플리케이션 등록 확인

애플리케이션이 정상적으로 등록되면 네이버 개발자 센터의 **[Application > 내 애플리케이션](https://developers.naver.com/apps/#/list)** 메뉴의 아래에 등록한 애플리케이션 이름으로 하위 메뉴가 생깁니다.

애플리케이션 이름을 클릭하면 **개요** 탭에서 애플리케이션에 부여된 클라이언트 아이디와 클라이언트 시크릿을 확인할 수 있습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-6.png)

## 클라이언트 아이디와 클라이언트 시크릿 확인

네이버 API를 호출할 때 클라이언트 아이디와 클라이언트 시크릿 값을 HTTP 헤더에 포함해서 전송해야 API를 호출할 수 있습니다.

클라이언트 시크릿 값은 클라이언트 아이디의 비밀번호와 같은 성격의 값입니다. 클라이언트 시크릿 값을 보려면 **Client Secret**에서 **보기**를 클릭합니다. **보기**를 클릭하면 버튼이 **재발급**으로 바뀝니다. **재발급**을 클릭하면 새로운 클라이언트 시크릿을 발급받을 수 있습니다.

![](https://developers.naver.com/proxyapi/rawgit/naver/naver-openapi-guide/master/ko/images/appregister-7.png)
