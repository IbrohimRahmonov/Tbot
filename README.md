# Tbot - 대학원 입시 도우미

한국 대학교 대학원 입시 정보를 제공하는 텔레그램 봇입니다.

## 기능

- 대학교별 입시 일정 조회
- 학과별 지원 요구사항 조회
- 대학원 홈페이지 링크 제공

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 봇 실행:
```bash
python bot.py
```

## 사용 방법

1. 텔레그램에서 봇과 대화 시작
2. `/start` 명령어로 봇 시작
3. 검색하고 싶은 대학 또는 학과 입력
   - 예: "연세대 일정"
   - 예: "고려대 컴퓨터"
   - 예: "카이스트 요구사항"

## 데이터 구조

`admissions.json` 파일에 대학원 입시 정보가 저장되어 있습니다:
- university: 대학교 이름
- department: 학과 이름
- schedule: 입시 일정
- requirements: 지원 요구사항
- website: 대학원 홈페이지
