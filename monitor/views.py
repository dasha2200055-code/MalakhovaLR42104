from django.shortcuts import render
import random

def index(request):
    apps = [
        {"name": "Telegram", "type": "Системное"},
        {"name": "WhatsApp", "type": "Системное"},
        {"name": "SystemUI", "type": "Системное"},
        {"name": "UnknownApp", "type": "Неизвестное"},
        {"name": "UnknownService", "type": "Неизвестное"},
    ]

    # Получаем пороги из запроса или берём по умолчанию
    req_threshold = int(request.GET.get('req_limit', 50))
    block_threshold = int(request.GET.get('block_limit', 2))

    results = []
    for app in apps:
        req = random.randint(1, 120)
        access = random.choice([0, 1])
        risk = 0

        if req > req_threshold:
            risk += 1
        if access == 1:
            risk += 1
        if "Unknown" in app["name"]:
            risk += 1

        status = "ЗАБЛОКИРОВАН" if risk >= block_threshold else "РАЗРЕШЁН"
       
        results.append({
            "name": app["name"],
            "type": app["type"],
            "requests": req,
            "access": "Есть" if access == 1 else "Нет",
            "risk": risk,
            "status": status,
        })

    blocked_count = sum(1 for r in results if r["status"] == "ЗАБЛОКИРОВАН")
    allowed_count = len(results) - blocked_count

    context = {
        "results": results,
        "blocked_count": blocked_count,
        "allowed_count": allowed_count,
        "checked_count": len(results),
        "req_limit": req_threshold,
        "block_limit": block_threshold,
    }

    return render(request, 'monitor/index.html', context)


def charts_page(request):
    apps = [
        {"name": "Telegram", "type": "Системное"},
        {"name": "WhatsApp", "type": "Системное"},
        {"name": "SystemUI", "type": "Системное"},
        {"name": "UnknownApp", "type": "Неизвестное"},
        {"name": "UnknownService", "type": "Неизвестное"},
    ]

    results = []
    for app in apps:
        req = random.randint(1, 120)
        access = random.choice([0, 1])
        risk = 0

        if req > 50:
            risk += 1
        if access == 1:
            risk += 1
        if "Unknown" in app["name"]:
            risk += 1

        status = "ЗАБЛОКИРОВАН" if risk >= 2 else "РАЗРЕШЁН"

        results.append({
            "name": app["name"],
            "requests": req,
            "access": access,
            "risk": risk,
            "status": status,
        })

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    charts = {}

    names = [r["name"] for r in results]
    requests = [r["requests"] for r in results]
    risks = [r["risk"] for r in results]
    blocked = sum(1 for r in results if r["status"] == "ЗАБЛОКИРОВАН")
    allowed = len(results) - blocked

    # График 1: Активность
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(1, 6), requests, marker='o', color='#3498db', linewidth=2)
    ax.set_title("Активность приложений (запросы)")
    ax.set_xlabel("ID")
    ax.set_ylabel("Запросы")
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    charts['activity'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # График 2: Риск
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ['#e74c3c' if r >= 2 else '#27ae60' for r in risks]
    ax.bar(range(1, 6), risks, color=colors)
    ax.set_title("Уровень риска")
    ax.set_xlabel("ID")
    ax.set_ylabel("Риск")
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    charts['risk'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # График 3: Круговая диаграмма
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie([allowed, blocked], labels=["РАЗРЕШЁН", "ЗАБЛОКИРОВАН"], autopct='%1.1f%%',
           colors=['#27ae60', '#e74c3c'], startangle=90, textprops={'fontsize': 14})
    ax.set_title("Распределение статусов", fontsize=16)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['pie'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # График 4: Риск по приложениям
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(names, risks, color=['#e74c3c' if r >= 2 else '#f39c12' if r == 1 else '#27ae60' for r in risks])
    ax.set_title("Риск по приложениям", fontsize=14)
    ax.set_ylabel("Уровень риска")
    plt.xticks(rotation=30, ha='right', fontsize=11)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    charts['bar_risk'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # График 5: Запросы по приложениям
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(names, requests, color='#3498db')
    ax.set_title("Запросы по приложениям", fontsize=14)
    ax.set_ylabel("Количество запросов")
    plt.xticks(rotation=30, ha='right', fontsize=11)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    charts['bar_requests'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    context = {
        "chart_activity": charts.get('activity', ''),
        "chart_risk": charts.get('risk', ''),
        "chart_pie": charts.get('pie', ''),
        "chart_bar_risk": charts.get('bar_risk', ''),
        "chart_bar_requests": charts.get('bar_requests', ''),
    }

    return render(request, 'monitor/charts.html', context)


def help_page(request):
    return render(request, 'monitor/help.html')


import csv
from django.http import HttpResponse

def download_csv(request):
    apps = [
        {"name": "Telegram", "type": "Системное"},
        {"name": "WhatsApp", "type": "Системное"},
        {"name": "SystemUI", "type": "Системное"},
        {"name": "UnknownApp", "type": "Неизвестное"},
        {"name": "UnknownService", "type": "Неизвестное"},
    ]

    results = []
    for app in apps:
        req = random.randint(1, 120)
        access = random.choice([0, 1])
        risk = 0
        if req > 50:
            risk += 1
        if access == 1:
            risk += 1
        if "Unknown" in app["name"]:
            risk += 1
        status = "ЗАБЛОКИРОВАН" if risk >= 2 else "РАЗРЕШЁН"
        results.append({
            "name": app["name"],
            "type": app["type"],
            "requests": req,
            "access": "Есть" if access == 1 else "Нет",
            "risk": risk,
            "status": status,
        })

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['№', 'Приложение', 'Тип', 'Запросов', 'Доступ к API', 'Уровень риска', 'Статус'])
    for i, r in enumerate(results, 1):
        writer.writerow([i, r['name'], r['type'], r['requests'], r['access'], r['risk'], r['status']])

    return response

from django.http import JsonResponse

def get_data(request):
    req_threshold = int(request.GET.get('req_limit', 50))
    block_threshold = int(request.GET.get('block_limit', 2))
    apps = [
        {"name": "Telegram", "type": "Системное"},
        {"name": "WhatsApp", "type": "Системное"},
        {"name": "SystemUI", "type": "Системное"},
        {"name": "UnknownApp", "type": "Неизвестное"},
        {"name": "UnknownService", "type": "Неизвестное"},
    ]

    results = []
    for app in apps:
        req = random.randint(1, 120)
        access = random.choice([0, 1])
        risk = 0
        if req > 50:
            risk += 1
        if access == 1:
            risk += 1
        if "Unknown" in app["name"]:
            risk += 1
        status = "ЗАБЛОКИРОВАН" if risk >= 2 else "РАЗРЕШЁН"
        results.append({
            "name": app["name"],
            "type": app["type"],
            "requests": req,
            "access": "Есть" if access == 1 else "Нет",
            "risk": risk,
            "status": status,
        })

    blocked_count = sum(1 for r in results if r["status"] == "ЗАБЛОКИРОВАН")
    allowed_count = len(results) - blocked_count

    return JsonResponse({
        "results": results,
        "blocked_count": blocked_count,
        "allowed_count": allowed_count,
        "checked_count": len(results),
        "req_limit": req_threshold,
        "block_limit": block_threshold,
    })