#!/usr/bin/env python
"""
Ejemplos de cómo usar la API
Ejecutar después de inicializar la BD y levantar el servidor
"""
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

BASE_URL = "http://localhost:8000"

# ==================== COLORES PARA TERMINAL ====================
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def print_header(text):
    print(f"\n{Color.HEADER}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Color.ENDC}\n")

def print_success(text):
    print(f"{Color.GREEN}✅ {text}{Color.ENDC}")

def print_info(text):
    print(f"{Color.CYAN}ℹ️  {text}{Color.ENDC}")

def print_error(text):
    print(f"{Color.RED}❌ {text}{Color.ENDC}")

# ==================== REGISTRO E LOGIN ====================

def test_registration():
    print_header("1. REGISTRO DE USUARIOS")
    
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if response.status_code == 200:
        print_success(f"Usuario registrado: {response.json()['username']}")
        return response.json()
    else:
        print_error(f"Error: {response.json()}")
        return None

def test_login():
    print_header("2. LOGIN")
    
    credentials = {
        "email": "juan@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['access_token']
        print_success(f"Login exitoso")
        print_info(f"Token: {token[:50]}...")
        return token
    else:
        print_error(f"Error: {response.json()}")
        return None

# ==================== FUNCIONES AUXILIARES ====================

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

def pretty_json(data):
    print(json.dumps(data, indent=2, default=str))

# ==================== TARJETAS Y CATEGORÍAS ====================

def test_create_card(token):
    print_header("3. CREAR TARJETA")
    
    card_data = {
        "name": "Visa Nueva",
        "card_type": "visa",
        "last_four": "9999"
    }
    
    response = requests.post(
        f"{BASE_URL}/cards",
        json=card_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        card = response.json()
        print_success(f"Tarjeta creada: {card['name']}")
        return card['id']
    else:
        print_error(f"Error: {response.json()}")
        return None

def test_list_cards(token):
    print_header("4. LISTAR TARJETAS")
    
    response = requests.get(
        f"{BASE_URL}/cards",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        cards = response.json()
        print_success(f"Total tarjetas: {len(cards)}")
        for card in cards:
            print(f"  - {card['name']} ({card['card_type']}) ...{card['last_four']}")
        return cards[0]['id'] if cards else None
    else:
        print_error(f"Error: {response.json()}")
        return None

def test_create_category(token):
    print_header("5. CREAR CATEGORÍA")
    
    category_data = {
        "name": "Restaurante Premium",
        "description": "Gastos en restaurantes caros",
        "color": "#FF5555",
        "icon": "🍽️"
    }
    
    response = requests.post(
        f"{BASE_URL}/categories",
        json=category_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        category = response.json()
        print_success(f"Categoría creada: {category['name']}")
        return category['id']
    else:
        print_error(f"Error: {response.json()}")
        return None

# ==================== GASTOS ====================

def test_create_expense_simple(token, card_id, category_id):
    print_header("6. CREAR GASTO SIMPLE (2 participantes)")
    
    expense_data = {
        "card_id": card_id,
        "category_id": category_id,
        "date": datetime.now().isoformat(),
        "concept": "Pizza con amigos",
        "total_amount": "150.00",
        "has_installments": False,
        "participants": [
            {
                "user_id": 1,
                "amount": "90.00",
                "description": "Mi parte"
            },
            {
                "user_id": 2,
                "amount": "60.00",
                "description": "Maria"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/expenses",
        json=expense_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        expense = response.json()
        print_success(f"Gasto creado: {expense['concept']} (${expense['total_amount']})")
        return expense['id']
    else:
        print_error(f"Error: {response.json()}")
        print(response.text)
        return None

def test_create_expense_with_installments(token, card_id, category_id):
    print_header("7. CREAR GASTO CON 3 CUOTAS (40/60%)")
    
    expense_data = {
        "card_id": card_id,
        "category_id": category_id,
        "date": (datetime.now() - timedelta(days=5)).isoformat(),
        "concept": "Viaje grupal (3 cuotas)",
        "total_amount": "600.00",
        "has_installments": True,
        "num_installments": 3,
        "participants": [
            {
                "user_id": 1,
                "percentage": "40.00"
            },
            {
                "user_id": 3,
                "percentage": "60.00"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/expenses",
        json=expense_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        expense = response.json()
        print_success(f"Gasto con cuotas creado: {expense['concept']}")
        print_info(f"Cuotas: {len(expense['installments'])}")
        return expense['id']
    else:
        print_error(f"Error: {response.json()}")
        print(response.text)
        return None

def test_list_expenses(token):
    print_header("8. LISTAR GASTOS")
    
    response = requests.get(
        f"{BASE_URL}/expenses",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        expenses = response.json()
        print_success(f"Total gastos: {len(expenses)}")
        for exp in expenses[:5]:  # Mostrar primeros 5
            print(f"  - {exp['concept']}: ${exp['total_amount']}")
        return expenses
    else:
        print_error(f"Error: {response.json()}")
        return None

# ==================== CUOTAS ====================

def test_get_pending_installments(token):
    print_header("9. CUOTAS PENDIENTES")
    
    response = requests.get(
        f"{BASE_URL}/installments/pending",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        installments = response.json()
        print_success(f"Cuotas pendientes: {len(installments)}")
        for inst in installments[:5]:
            print(f"  - Cuota #{inst['installment_number']}: ${inst['amount']}")
    else:
        print_error(f"Error: {response.json()}")

def test_get_my_pending_splits(token):
    print_header("10. MIS CUOTAS PARA PAGAR")
    
    response = requests.get(
        f"{BASE_URL}/installments/my-splits/pending",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        splits = response.json()
        print_success(f"Mis cuotas pendientes: {len(splits)}")
        for split in splits[:5]:
            print(f"  - {split['concept']}: ${split['amount']} (vence {split['due_date'][:10]})")
    else:
        print_error(f"Error: {response.json()}")

# ==================== PAGOS ====================

def test_create_payment(token):
    print_header("11. REGISTRAR PAGO")
    
    payment_data = {
        "to_user_id": 2,
        "amount": "100.00",
        "description": "Pago por cena del 15/1",
        "payment_method": "transferencia"
    }
    
    response = requests.post(
        f"{BASE_URL}/payments",
        json=payment_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        payment = response.json()
        print_success(f"Pago registrado: ${payment['amount']}")
    else:
        print_error(f"Error: {response.json()}")

def test_get_my_debts(token):
    print_header("12. DEUDAS (LO QUE DEBO)")
    
    response = requests.get(
        f"{BASE_URL}/payments/me/owe",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        debts = response.json()
        print_success(f"Deudas: {len(debts)}")
        total = sum(Decimal(d['amount']) for d in debts)
        print_info(f"Total que debo: ${total}")
        for debt in debts[:5]:
            print(f"  - Le debo a {debt['to_user_name']}: ${debt['amount']} ({debt['concept']})")
    else:
        print_error(f"Error: {response.json()}")

def test_get_my_credits(token):
    print_header("13. CRÉDITOS (LO QUE ME DEBEN)")
    
    response = requests.get(
        f"{BASE_URL}/payments/me/owed",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        credits = response.json()
        print_success(f"Créditos: {len(credits)}")
        total = sum(Decimal(c['amount']) for c in credits)
        print_info(f"Total que me deben: ${total}")
        for credit in credits[:5]:
            print(f"  - Me debe {credit['from_user_name']}: ${credit['amount']} ({credit['concept']})")
    else:
        print_error(f"Error: {response.json()}")

# ==================== REPORTES ====================

def test_get_monthly_report(token):
    print_header("14. REPORTE MENSUAL")
    
    now = datetime.now()
    response = requests.get(
        f"{BASE_URL}/reports/monthly/{now.year}/{now.month}",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        report = response.json()
        print_success(f"Reporte de {report['month']}/{report['year']}")
        print_info(f"Total gastado (mi parte): ${report['total_spent']}")
        print_info(f"Total en tarjetas: ${report['total_in_cards']}")
        print("\nPor categoría:")
        for cat in report['by_category']:
            print(f"  - {cat['category_name']}: ${cat['total']} ({cat['count']} gastos)")
    else:
        print_error(f"Error: {response.json()}")

def test_get_statistics(token):
    print_header("15. ESTADÍSTICAS GENERALES")
    
    response = requests.get(
        f"{BASE_URL}/reports/statistics",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Estadísticas del usuario")
        print_info(f"Total gastado (todos los tiempos): ${stats['total_all_time']}")
        print_info(f"Cantidad de gastos: {stats['total_expenses']}")
        print_info(f"Tarjetas: {stats['total_cards']}")
        print_info(f"Categorías: {stats['total_categories']}")
        print_info(f"Cuotas pendientes: {stats['pending_installments']}")
    else:
        print_error(f"Error: {response.json()}")

# ==================== MAIN ====================

def main():
    print(f"\n{Color.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         EJEMPLOS DE USO - GASTOS APP API                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Color.ENDC}")
    
    # Login
    token = test_login()
    if not token:
        print_error("No se pudo obtener token, abortando")
        return
    
    # Obtener tarjeta y categoría
    card_id = test_list_cards(token)
    category_id = test_create_category(token)
    
    if not card_id or not category_id:
        print_error("No se pudo obtener tarjeta o categoría")
        return
    
    # Tests
    test_create_expense_simple(token, card_id, category_id)
    test_create_expense_with_installments(token, card_id, category_id)
    test_list_expenses(token)
    test_get_pending_installments(token)
    test_get_my_pending_splits(token)
    test_get_my_debts(token)
    test_get_my_credits(token)
    test_create_payment(token)
    test_get_monthly_report(token)
    test_get_statistics(token)
    
    print(f"\n{Color.GREEN}✅ Pruebas completadas{Color.ENDC}\n")

if __name__ == "__main__":
    main()
