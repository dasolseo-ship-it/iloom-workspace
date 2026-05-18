# iloom Web Style Guide

## 1. Design Philosophy: "Design with Reason"

일룸의 디자인 철학은 "이유있는 디자인"입니다. 처음에는 평범해 보이지만 사용하면서 발견되는 정교한 설계, 기능에 근거한 디자인을 추구합니다. 웹에서도 이 철학을 반영하여 화려한 장식보다 콘텐츠와 제품 자체에 집중할 수 있는 환경을 만듭니다. 모던 미니멀리즘을 기반으로, 따뜻함과 기능성이 공존하는 "Quiet Luxury" 톤을 유지합니다.

## 2. Core Theme: Modern Warm Minimalism

제품 카탈로그가 아니라, 완성된 공간에서의 라이프스타일을 보여주는 플랫폼으로 느껴져야 합니다. 일룸의 브랜드명(illuminate + room)처럼, 공간에 빛을 더하는 경험을 전달합니다.

**Tone & Manner**: 모던한, 절제된, 따뜻한, 신뢰할 수 있는, 세련된, 기능적인

## 3. Color Palette

### Brand Colors

| Role | Name | HEX | Usage |
|------|------|-----|-------|
| Primary (Brand Red) | Deep Red | `#c80a1e` | 핵심 CTA 버튼, 활성 탭, 가격 강조, 선택 상태 |
| Background (Main) | White | `#FFFFFF` | 메인 페이지 배경, 카드 배경 |
| Background (Alt) | Light Gray | `#F8F8F8` | 섹션 구분 배경, 아이콘 배경 |

### Neutral Colors

| Role | Name | HEX | Usage |
|------|------|-----|-------|
| Text Primary | Dark Gray | `#333333` | 본문 텍스트, 상품명 (순검정 대신 사용) |
| Text Secondary | Medium Gray | `#999999` | 보조 텍스트, 메타 정보, 라벨 |
| Border / Divider | Light Gray | `#E0E0E0` | 카드 테두리, 구분선, 비활성 요소 |

### Product Mood Colors (참고용)

제품 라인별 무드 카테고리에서 파생된 보조 색상입니다. 메인 UI가 아닌 라이프스타일 콘텐츠, 배너, 캠페인 페이지에서 활용합니다.

| Category | Tone | Usage |
|----------|------|-------|
| CLASSIC | Warm wood, dark brown tones | 프리미엄 라인, 침실 |
| CASUAL | Soft neutral, warm beige | 일반 라이프스타일 |
| POP | Vivid accent colors | 키즈/학생 라인 |
| NATURAL | Muted green, earth tones | 친환경, 원목 라인 |

## 4. Typography

전체 sans-serif 체계로, 한국어와 영문의 조합을 통해 모던하고 깔끔한 인상을 줍니다.

### Font Stack

| Purpose | Font | Source | Note |
|---------|------|--------|------|
| Korean (UI 전체) | Noto Sans KR | Google Fonts | 본문, 라벨, 메뉴 등 |
| English (Display) | Montserrat | Google Fonts | 로고, 헤더, 가격 등 |

### Font Weights (Montserrat)

Thin(100), Light(300), Regular(400), Medium(500), Bold(700), Black(900) -- 9개 웨이트 전체 로드

### Hierarchy

| Level | Font | Weight | Size | Note |
|-------|------|--------|------|------|
| H1 (Page Title) | Montserrat + Noto Sans KR | Bold (700) | 32px | 페이지 최상위 제목 |
| H2 (Section Title) | Montserrat + Noto Sans KR | SemiBold (600) | 24px | 섹션 구분 |
| H3 (Card Title) | Noto Sans KR | Medium (500) | 18px | 상품명, 카드 제목 |
| Body | Noto Sans KR | Regular (400) | 16px | 행간 1.6배, 자간 -0.2px |
| Label / Meta | Noto Sans KR | Regular (400) | 14px | 보조 정보, `#999999` 색상 |
| Price | Montserrat | Bold (700) | 18-20px | `#c80a1e` 강조 |
| Small | Noto Sans KR | Regular (400) | 12px | 약관, 각주 |

## 5. Layout & Components

### Grid System

| Property | Value |
|----------|-------|
| Min Width (Desktop) | 1200px |
| Product Grid | 4 columns |
| Gutter | 20-24px (추정) |
| Content Max Width | 1200px, center aligned |

### Cards (Product)

상품 카드는 일룸 UI의 핵심 단위입니다.

```
Structure:
+---------------------------+
|                           |
|     Product Image         |  <- hover 시 secondary 이미지로 교체
|                           |
+---------------------------+
| Brand Name (sub label)    |  <- #999999, 14px
| Product Name              |  <- #333333, 16px, Medium
| Price (할인가)             |  <- #c80a1e, Bold
| Price (정상가)             |  <- #999999, line-through
| Wishlist Count (heart)    |  <- heart icon + count
+---------------------------+
```

- `border-radius`: 0px (사각형, 미니멀)
- `box-shadow`: 없음 (플랫 디자인)
- `border`: 없음 또는 `1px solid #E0E0E0`
- Hover: 이미지 스왑 (primary -> secondary 이미지)

### Buttons

| Type | Background | Text | Border | Usage |
|------|-----------|------|--------|-------|
| Primary CTA | `#c80a1e` | `#FFFFFF` | none | "구매하기", "장바구니" |
| Secondary | `#FFFFFF` | `#333333` | `1px solid #E0E0E0` | "취소", "목록" |
| Text Button | transparent | `#333333` | none | 필터, 정렬 옵션 |
| Active State | transparent | `#c80a1e` | none | 선택된 필터/탭 |

### Navigation

- **GNB (Global Navigation Bar)**: 상단 고정, 로고 좌측, 카테고리 중앙, 유틸리티 우측
- **Category Depth**: 대분류 > 중분류 > 소분류 (드롭다운 계층형)
- **카테고리**: 침실 / 드레스룸 / 거실 / 주방 / 아이방 / 학생방 / 서재 / 조명 / 반려동물
- **최근 본 상품 위젯**: 우측 플로팅, 접기/펼치기 가능

### Filter & Sort

- 필터: 텍스트 링크 스타일 (버튼 배경 없음)
- 활성 필터: 텍스트 색상 `#c80a1e`로 전환
- 정렬 옵션: "인기순 / 신상품순 / 가격순 / 상품평순"

## 6. Iconography

- **Style**: 라인(Line) 아이콘, 1-1.5px stroke
- **Shape**: 직선적이고 기하학적 (둥근 모서리 최소화)
- **Core Icons**:
  - Wishlist: Heart (empty/filled 토글)
  - Cart: Shopping bag
  - Search: Magnifying glass
  - User: Person outline
  - Share: Share icon
- **Recommended Set**: 기본 시스템 아이콘 또는 커스텀 SVG (일룸 자체 아이콘셋 사용)

## 7. Photography Style

일룸 비주얼의 핵심은 "라이프스타일 룸 스테이징"입니다.

| Aspect | Guideline |
|--------|-----------|
| Primary Shot | 완성된 인테리어 공간 안에서의 제품 (단독 제품컷 X) |
| Background | 화이트/뉴트럴 톤 공간, 자연광 느낌 |
| Texture | 원목, 패브릭, 식물 등 자연 소재 강조 |
| Color Tone | 따뜻한 뉴트럴 (warm white, beige, wood) |
| Accent | 소프트 블루, 블러시 핑크, 그린 등 공간 소품으로 포인트 |
| People | 셀럽 캠페인 시 활용 (2024: 변우석), 일반 상품은 공간 중심 |
| Crop | 공간 전체를 보여주는 와이드 컷 + 디테일 클로즈업 조합 |

## 8. Interactions (Micro-interactions)

| Interaction | Spec |
|-------------|------|
| Card Hover | 이미지 교체 (primary -> secondary), transition 0.3s |
| Button Hover | opacity 0.85 또는 미세한 색상 변화 |
| Tab Active | 텍스트 색상 `#c80a1e` + underline 또는 bold 전환 |
| Wishlist Toggle | Heart empty/filled 애니메이션 |
| Page Transition | 부드러운 fade-in (0.2-0.3s) |
| Loading | 심플 스피너 (브랜드 장식 없음, 미니멀 유지) |
| Toast / Feedback | 상단 또는 중앙 토스트, 2-3초 후 자동 소멸 |

## 9. Logo

| Property | Value |
|----------|-------|
| Text | "iloom" (전소문자) |
| Color | `#c80a1e` (Deep Red) on white/transparent |
| Etymology | illuminate + room |
| Minimum Size | 85px width (웹 기준) |
| Clear Space | 로고 높이의 50% 이상 여백 확보 |
| Tagline | "일상에 새로운 설렘과 다채로운 가치를 더하는" |

## 10. Responsive Breakpoints (추정)

| Breakpoint | Width | Grid Columns |
|------------|-------|-------------|
| Mobile | ~479px | 1-2 columns |
| Tablet | 480-767px | 2 columns |
| Desktop (sm) | 768-1199px | 3 columns |
| Desktop (lg) | 1200px+ | 4 columns |

> Note: 모바일 breakpoint은 공식 확인 필요. 위 값은 일반적 커머스 패턴 기반 추정치입니다.

---

## Summary

이 스타일 가이드는 일룸의 "이유있는 디자인" 철학을 웹에 반영합니다. 딥레드(`#c80a1e`) 단일 브랜드 컬러와 Noto Sans KR + Montserrat 폰트 조합, 그리고 화이트/그레이 뉴트럴 배경 위에 라이프스타일 포토그래피가 중심이 되는 구조입니다. 장식을 최소화하고 콘텐츠(제품과 공간)가 주인공이 되도록 절제된 UI를 유지하는 것이 핵심입니다.

---

### Limitations

- `#c80a1e` vs `#c80818`: 소스에 따라 미세한 차이 존재. 브라우저 Color Picker로 직접 확인 권장.
- 공식 브랜드 가이드라인(PDF)은 공개되어 있지 않음. 일룸 마케팅팀(1577-5670) 문의 시 확보 가능.
- 모바일 breakpoint 및 반응형 상세값은 추정치.
- CSS 변수, 정확한 spacing scale(4px/8px 등)은 CDN 접근 불가로 미확인.
