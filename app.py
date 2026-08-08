import base64
import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="장비 트러블슈팅 가이드북 자동 생성기",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 장비별 트러블슈팅 리포트 자동 생성 앱")
st.markdown(
    "현장에서 입력한 데이터와 사진을 바탕으로 **표준화된 [FIELD SERVICE] 가이드북 문서**를"
    " 자동 생성하고 **PDF/인쇄 및 파일 저장**합니다."
)

# Sidebar - Settings
st.sidebar.header("📋 작성자 설정")
author_name = st.sidebar.text_input("작성자 이름", value="김상룡 과장")
doc_prefix = st.sidebar.text_input("문서 번호 접두사", value="TS-2026")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 사용 방법")
st.sidebar.info(
    "1. 본문의 각 항목에 현장 고장 조치 내역을 입력합니다.\n2. 현장 사진(PNG,"
    " JPG 등)을 업로드합니다.\n3. **[🚀 리포트 생성 및 미리보기]** 버튼을"
    " 누릅니다.\n4. 완성된 리포트 아래의 **[🖨️ 바로 인쇄 / PDF 저장]** 또는"
    " **[💾 HTML 문서 다운로드]** 버튼을 클릭합니다."
)

# Form Sections
st.subheader("1. 고장 및 장비 기본 정보 (Basic Information)")
col1, col2, col3 = st.columns(3)

with col1:
  doc_no = st.text_input("문서 번호", value=f"{doc_prefix}-001")
  client_name = st.text_input("고객사 / 지역", value="현대자동차 / 울산")
  equip_type = st.radio(
      "장비 구분",
      ["CT (VoluMax/METROTOM)", "CMM (3차원측정기)"],
      index=0,
  )

with col2:
  write_date = st.date_input("작성일자", datetime.date.today())
  equip_name = st.text_input("장비명 / S/N", value="VoluMax / SN: 123456")
  severity = st.selectbox(
      "심각도 (Severity)",
      ["CRITICAL (라인중단)", "MAJOR (품질/기능이상)", "MINOR (단순경고)"],
  )

with col3:
  occur_time = st.text_input(
      "발생 일시", value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
  )
  complete_time = st.text_input(
      "조치 완료일 및 소요시간",
      value=(
          f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (소요:"
          " 2.0h)"
      ),
  )

st.markdown("---")
st.subheader("2. 고장 현상 및 에러 로그 (Symptom & Error Log)")
symptom_desc = st.text_area(
    "■ 고장 현상 설명",
    value=(
        "스캔 진행 중 특정 축 구동 시 이음 발생 후 Interlock 스톱. S/W"
        " 재부팅 후에도 동일 에러 재발."
    ),
)
error_code_log = st.text_area(
    "■ Error Code / System Log Message",
    value=(
        "ERROR CODE: ERR_X_DRIVE_TIMEOUT (0x80041002)\nMESSAGE: X-Axis Drive"
        " Amplifier Overcurrent / Position Limit Reached\nSYSTEM STATUS:"
        " Emergency Stop Triggered by Controller Hardware Interlock"
    ),
)

st.markdown("---")
st.subheader("3. 현장 사진 및 에러 캡처 업로드 (Photos)")
st.caption("📷 PNG, JPG, JPEG 파일 모두 업로드 가능합니다. (최소 2~3장 업로드 권장)")

uploaded_files = st.file_uploader(
    "현장 사진 업로드 (에러 화면, 교체 부품, 현장 상황 등)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

image_b64_list = []
if uploaded_files:
  num_files = len(uploaded_files)
  num_cols = min(num_files, 3) if num_files > 0 else 1
  cols = st.columns(num_cols)

  for idx, file in enumerate(uploaded_files):
    bytes_data = file.read()
    b64_str = base64.b64encode(bytes_data).decode()
    ext = file.name.split(".")[-1].lower()
    mime_type = "image/png" if ext == "png" else "image/jpeg"
    image_b64_list.append((file.name, b64_str, mime_type))

    with cols[idx % num_cols]:
      st.image(
          bytes_data,
          caption=f"사진 {idx+1}: {file.name}",
          use_container_width=True,
      )

st.markdown("---")
st.subheader("4. 원인 분석 (Root Cause Analysis)")
rca_col1, rca_col2, rca_col3 = st.columns(3)
with rca_col1:
  hw_cause = st.text_input(
      "하드웨어 (HW) 원인",
      value="X축 드라이브 모터 케이블 접촉 불량 또는 벨트 장력 저하",
  )
with rca_col2:
  pwr_cause = st.text_input(
      "전단 파워 / 보드 원인",
      value="AMP 보드 과전류 발생에 따른 인버터 보드 릴레이 다운",
  )
with rca_col3:
  sw_cause = st.text_input(
      "소프트웨어 / 파라미터 원인", value="Limit Switch 파라미터 오프셋 값 변형"
  )

st.markdown("---")
st.subheader("5. 조치 절차 (Step-by-Step SOP)")
sop_steps = st.text_area(
    "조치 절차 (한 줄에 1단계씩 입력)",
    value=(
        "1. 안전 조치 및 전원 차단: 장비 Main Breaker 차단 및 LOTO 체결\n2."
        " 컨트롤러 점검: Controller Rear Panel 개폐 후 AMP 보드 상태 확인\n3."
        " 파트 교체: 손상된 Drive AMP Board 신규 파트로 교체 진행\n4. Zero"
        " Point Calibration: S/W 내 Drive Parameter Reload 후 참조점 재설정\n5."
        " 시운전: 10회 연속 Repeatability Test 수행 완료"
    ),
)

st.markdown("---")
st.subheader("6. 사용 부품 및 꿀팁 (Part List & Field Tip)")
part_col1, part_col2 = st.columns(2)
with part_col1:
  part_info = st.text_area(
      "교체 파트 정보 (부품명 / P/N / 수량 / 비고)",
      value=(
          "X-Drive Amplifier Board | SE0700356 | 1 EA | 창원 사무실 재고\nSignal"
          " Cable (X-Axis) | SE0300344 | 1 EA | 예비용 재배선"
      ),
  )
with part_col2:
  field_tip = st.text_area(
      "💡 엔지니어 꿀팁 & 재발 방지책",
      value=(
          "- Board 교체 전 반드시 Cable 접지 상태를 먼저 확인할 것 (가짜"
          " 과전류 에러 방지).\n- 정기 점검 시 X축 케이블 베어 내부 마모"
          " 여부 필수 체크."
      ),
  )

# Report Generation
if st.button("🚀 정해진 양식대로 리포트 생성하기", type="primary"):
  st.success("양식 규칙에 맞춰 깔끔하게 생성되었습니다!")

  sop_list = [line.strip() for line in sop_steps.split("\n") if line.strip()]
  sop_html = "".join([f"<li>{step}</li>" for step in sop_list])

  parts_list = [line.split("|") for line in part_info.split("\n") if line.strip()]
  parts_rows_html = ""
  for p in parts_list:
    p_name = p[0].strip() if len(p) > 0 else "-"
    p_pn = p[1].strip() if len(p) > 1 else "-"
    p_qty = p[2].strip() if len(p) > 2 else "-"
    p_note = p[3].strip() if len(p) > 3 else "-"
    parts_rows_html += (
        f"<tr><td>{p_name}</td><td"
        f" style='text-align:center;'>{p_pn}</td><td"
        f" style='text-align:center;'>{p_qty}</td><td>{p_note}</td></tr>"
    )

  img_gallery_html = ""
  if image_b64_list:
    img_gallery_html = (
        "<div class='section-title'>3. 현장 사진 및 에러 캡처 (Photos)</div><div"
        " style='display:grid; grid-template-columns: repeat(3, 1fr);"
        " gap:12px; margin-bottom:20px;'>"
    )
    for img_idx, (img_name, b64_str, mime_type) in enumerate(image_b64_list):
      img_gallery_html += (
          "<div style='border:1px solid #cbd5e1; padding:8px;"
          " border-radius:6px; background:#f8fafc; text-align:center;'><img"
          f" src='data:{mime_type};base64,{b64_str}' style='width:100%;"
          " max-height:220px; object-fit:contain; border-radius:4px;'><br><span"
          " style='font-size:8.5pt; color:#475569; font-weight:bold;"
          f" margin-top:4px; display:block;'>[사진 {img_idx+1}]"
          f" {img_name}</span></div>"
      )
    img_gallery_html += "</div>"

  formatted_field_tip = field_tip.replace("\n", "<br>")

  report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; color: #1e293b; background: #ffffff; margin:0; padding:15px; }}
        .header {{ background: #0f172a; color: #38bdf8; padding: 15px 20px; border-radius: 6px; margin-bottom: 20px; }}
        .section-title {{ color: #0369a1; border-left: 4px solid #0284c7; padding-left: 8px; margin-top: 20px; margin-bottom: 10px; font-size: 13pt; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 9.5pt; }}
        th, td {{ padding: 8px; border: 1px solid #e2e8f0; text-align: left; }}
        .bg-gray {{ background: #f8fafc; }}
        .bg-blue {{ background: #0284c7; color: #ffffff; }}
        .log-box {{ background: #1e293b; color: #38bdf8; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 9pt; white-space: pre-wrap; }}
        .tip-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 4px; color: #166534; font-size: 9.5pt; }}
        .btn-toolbar {{ margin-bottom: 15px; display: flex; gap: 10px; }}
        .btn-print {{ background: #0284c7; color: #ffffff; border: none; padding: 10px 18px; border-radius: 6px; font-size: 10pt; font-weight: bold; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }}
        .btn-print:hover {{ background: #0369a1; }}
        @media print {{
            .btn-toolbar {{ display: none !important; }}
            body {{ padding: 0; }}
        }}
    </style>
    </head>
    <body>
        <div class="btn-toolbar">
            <button class="btn-print" onclick="window.print()">🖨️ 리포트 바로 인쇄 / PDF 저장</button>
        </div>

        <div class="header">
            <h2 style="margin:0; font-size:18pt;">[FIELD SERVICE] 장비별 트러블슈팅 리포트</h2>
            <p style="margin:4px 0 0 0; color:#94a3b8; font-size:10pt;">CT & CMM 현장 조치 및 고장 이력 관리 표준 가이드북 문서</p>
        </div>

        <div class="section-title">1. 고장 및 장비 기본 정보</div>
        <table>
            <tr class="bg-gray">
                <th style="width:15%;">문서 번호</th><td>{doc_no}</td>
                <th style="width:15%;">작성일 / 작성자</th><td>{write_date} / {author_name}</td>
            </tr>
            <tr>
                <th class="bg-gray">고객사 / 지역</th><td>{client_name}</td>
                <th class="bg-gray">장비명 / S/N</th><td>{equip_name}</td>
            </tr>
            <tr class="bg-gray">
                <th>장비 구분</th><td>{equip_type}</td>
                <th>심각도</th><td><b style="color:#ef4444;">{severity}</b></td>
            </tr>
            <tr>
                <th class="bg-gray">발생 일시</th><td>{occur_time}</td>
                <th class="bg-gray">조치 완료일</th><td>{complete_time}</td>
            </tr>
        </table>

        <div class="section-title">2. 고장 현상 및 에러 로그</div>
        <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:10px; border-radius:4px; margin-bottom:15px; font-size:9.5pt;">
            <b>■ 고장 현상:</b> {symptom_desc}<br><br>
            <b>■ Error Code / System Log:</b>
            <div class="log-box">{error_code_log}</div>
        </div>

        {img_gallery_html}

        <div class="section-title">4. 원인 분석 (Root Cause Analysis)</div>
        <table>
            <tr class="bg-blue"><th style="width:25%;">분류</th><th>추정 원인</th></tr>
            <tr><td class="bg-gray"><b>하드웨어 (HW)</b></td><td>{hw_cause}</td></tr>
            <tr><td class="bg-gray"><b>전단 파워 / 보드</b></td><td>{pwr_cause}</td></tr>
            <tr><td class="bg-gray"><b>소프트웨어 / 파라미터</b></td><td>{sw_cause}</td></tr>
        </table>

        <div class="section-title">5. 조치 절차 (SOP)</div>
        <ol style="font-size:9.5pt; line-height:1.6; margin-bottom:15px;">{sop_html}</ol>

        <div class="section-title">6. 사용 부품 및 꿀팁</div>
        <table>
            <tr class="bg-blue"><th style="width:30%;">부품명</th><th style="width:25%; text-align:center;">P/N</th><th style="width:15%; text-align:center;">수량</th><th>비고</th></tr>
            {parts_rows_html}
        </table>

        <div class="tip-box">
            <b>💡 엔지니어 꿀팁 & 재발 방지책:</b><br>{formatted_field_tip}
        </div>
    </body>
    </html>
    """

  st.download_button(
      label="💾 완제품 문서 파일(.html)로 저장하기",
      data=report_html,
      file_name=f"{doc_no}_트러블슈팅_리포트.html",
      mime="text/html",
  )

  calc_height = 1150 + (300 if image_b64_list else 0)
  components.html(report_html, height=calc_height, scrolling=True)