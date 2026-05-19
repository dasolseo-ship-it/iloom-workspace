# 동쭐커플 대시보드 💛💙

> 다쭐 & 동쭐의 실시간 공유 대시보드

---

## Firebase 설정 가이드 (처음 한 번만)

### 1단계 — Firebase 프로젝트 만들기

1. [firebase.google.com](https://firebase.google.com) 접속 → 구글 계정으로 로그인
2. **콘솔로 이동** 클릭
3. **프로젝트 추가** 클릭
4. 프로젝트 이름 입력 (예: `dongzzul-couple`)
5. Google Analytics → **사용 설정 해제** 후 **프로젝트 만들기**

---

### 2단계 — 웹 앱 등록 & 설정값 복사

1. 프로젝트 홈에서 `</>` (웹) 아이콘 클릭
2. 앱 이름 입력 (예: `couple-dashboard`)
3. **Firebase 호스팅도 설정** 체크박스 ✅ 체크
4. **앱 등록** 클릭
5. 아래처럼 생긴 코드가 보이면 전체 복사:

```js
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "dongzzul-couple.firebaseapp.com",
  projectId: "dongzzul-couple",
  storageBucket: "dongzzul-couple.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};
```

6. `index.html` 열어서 아래 부분에 붙여넣기:

```js
// 🔧 여기에 Firebase 설정값을 붙여 넣으세요
const firebaseConfig = {
  apiKey:            "← 여기",
  ...
};
```

---

### 3단계 — Firestore 데이터베이스 활성화

1. Firebase 콘솔 왼쪽 메뉴 → **Firestore Database** 클릭
2. **데이터베이스 만들기** 클릭
3. **테스트 모드로 시작** 선택 → 다음
4. 위치: **asia-northeast3 (서울)** 선택 → **완료**
5. 잠시 기다리면 데이터베이스 생성 완료

---

### 4단계 — Firebase Hosting으로 배포 (URL 발급)

> Node.js 가 필요합니다. [nodejs.org](https://nodejs.org) 에서 LTS 버전 설치.

PowerShell에서 아래 명령어를 순서대로 실행:

```powershell
# Firebase CLI 설치 (최초 1회)
npm install -g firebase-tools

# 로그인
firebase login

# 프로젝트 폴더로 이동
cd "C:\Users\FURSYS\Downloads\iloom-workspace-claude\10-projects\동쭐커플-대시보드"

# Firebase 초기화
firebase init hosting
```

`firebase init hosting` 실행 시 질문 답변:

| 질문 | 답변 |
|------|------|
| Which project? | 방금 만든 `dongzzul-couple` 선택 |
| Public directory? | `.` 입력 (현재 폴더) |
| Configure as SPA? | `N` |
| Set up automatic builds? | `N` |

```powershell
# 배포!
firebase deploy --only hosting
```

완료되면 터미널에 URL이 나타납니다:
```
Hosting URL: https://dongzzul-couple.web.app
```

**이 URL을 오빠한테 공유하면 끝!** 🎉

---

### 5단계 — 내용 수정 후 재배포

`index.html` 수정할 때마다:

```powershell
cd "C:\Users\FURSYS\Downloads\iloom-workspace-claude\10-projects\동쭐커플-대시보드"
firebase deploy --only hosting
```

---

## 기능 요약

| 기능 | 설명 |
|------|------|
| D-Day | 3월 22일부터 오늘까지 자동 계산 |
| 기념일 | D+100, 200, 300, 1주년... 동근/다솔 생일 자동 표시 |
| 공유 캘린더 | 날짜 클릭 → 일정 추가/삭제, 실시간 동기화 |
| 색상 구분 | 다솔 💛 노란색 · 동근 💙 하늘색 |
| 실시간 동기화 | Firestore `onSnapshot` — 한 명이 등록하면 상대방 화면 즉시 갱신 |

---

## 파일 구조

```
동쭐커플-대시보드/
├── index.html     ← 전체 앱 (단일 파일)
├── README.md      ← 이 파일 (설정 가이드)
├── .firebaserc    ← firebase init 후 자동 생성
└── firebase.json  ← firebase init 후 자동 생성
```
