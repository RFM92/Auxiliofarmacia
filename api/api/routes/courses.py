"""
Routes: Courses
Endpoints para o Hub de Cursos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..dependencies import get_current_user, get_optional_user
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/courses", tags=["Courses"])


# ========== SCHEMAS ==========
class CourseResponse(BaseModel):
    id: str
    title: str
    cat: str
    desc: str
    color: str
    color2: str
    badge: str
    thumb: str
    duration: str
    modules: int
    lessons: int
    price: float
    price_old: float


class CourseEnrollment(BaseModel):
    course_id: str
    enrolled_at: datetime
    progress: int = 0
    completed_modules: List[int] = []


class ProgressUpdate(BaseModel):
    module_index: int
    completed: bool


class CertificateResponse(BaseModel):
    course_id: str
    course_title: str
    user_name: str
    issued_at: datetime
    certificate_id: str
    hours: int
    validation_url: str


class BundlePurchase(BaseModel):
    bundle_id: str
    payment_id: Optional[str] = None


# ========== DATA (em produção viria do DB) ==========
COURSES_DATA = {
    'antibioticos': {
        'id': 'antibioticos', 'title': 'Antibioticoterapia na Pratica Clinica',
        'cat': 'Classe Terapeutica', 'color': '#dc2626', 'color2': '#f59e0b',
        'badge': 'MAIS VENDIDO', 'thumb': '🦠', 'duration': '8h 30min',
        'modules': 12, 'lessons': 48, 'price': 197.0, 'price_old': 297.0,
        'desc': 'Curso completo sobre uso racional de antibioticos.'
    },
    'aines': {
        'id': 'aines', 'title': 'AINEs: Do Mecanismo a Escolha Clinica',
        'cat': 'Classe Terapeutica', 'color': '#7c3aed', 'color2': '#a855f7',
        'badge': 'ATUALIZADO', 'thumb': '💊', 'duration': '6h 15min',
        'modules': 10, 'lessons': 36, 'price': 147.0, 'price_old': 197.0,
        'desc': 'Domine anti-inflamatorios nao esteroidais.'
    },
    'analgesicos': {
        'id': 'analgesicos', 'title': 'Analgesicos e Dor',
        'cat': 'Classe Terapeutica', 'color': '#0d9488', 'color2': '#06b6d4',
        'badge': 'RECOMENDADO', 'thumb': '⚡', 'duration': '7h',
        'modules': 11, 'lessons': 40, 'price': 167.0, 'price_old': 247.0,
        'desc': 'Manejo farmacologico da dor.'
    },
    'antihipertensivos': {
        'id': 'antihipertensivos', 'title': 'Anti-hipertensivos',
        'cat': 'Classe Terapeutica', 'color': '#dc2626', 'color2': '#ec4899',
        'badge': 'COMPLETO', 'thumb': '❤️', 'duration': '9h',
        'modules': 14, 'lessons': 52, 'price': 197.0, 'price_old': 297.0,
        'desc': 'Drogas anti-hipertensivas em detalhes.'
    },
    'diabeticos': {
        'id': 'diabeticos', 'title': 'Antidiabeticos',
        'cat': 'Classe Terapeutica', 'color': '#f59e0b', 'color2': '#eab308',
        'badge': 'PRATICO', 'thumb': '🩸', 'duration': '7h 30min',
        'modules': 12, 'lessons': 44, 'price': 177.0, 'price_old': 247.0,
        'desc': 'Manejo farmacologico do diabetes.'
    },
    'psicotropicos': {
        'id': 'psicotropicos', 'title': 'Psicotropicos',
        'cat': 'Classe Terapeutica', 'color': '#6366f1', 'color2': '#8b5cf6',
        'badge': 'LEGAL', 'thumb': '🧠', 'duration': '8h',
        'modules': 12, 'lessons': 45, 'price': 197.0, 'price_old': 297.0,
        'desc': 'Prescricao segura e legal.'
    },
    'corticoides': {
        'id': 'corticoides', 'title': 'Corticoides',
        'cat': 'Classe Terapeutica', 'color': '#0891b2', 'color2': '#06b6d4',
        'badge': 'CLASSICO', 'thumb': '💉', 'duration': '5h 45min',
        'modules': 9, 'lessons': 32, 'price': 127.0, 'price_old': 197.0,
        'desc': 'Uso clinico e manejo de efeitos.'
    },
    'anticoagulantes': {
        'id': 'anticoagulantes', 'title': 'Anticoagulantes e Antiagregantes',
        'cat': 'Classe Terapeutica', 'color': '#be123c', 'color2': '#f43f5e',
        'badge': 'AVANCADO', 'thumb': '🩸', 'duration': '6h 30min',
        'modules': 10, 'lessons': 38, 'price': 167.0, 'price_old': 247.0,
        'desc': 'Terapia anticoagulante avancada.'
    },
}

BUNDLES = {
    'curso_pro': {
        'id': 'curso_pro', 'title': 'Curso + Dashboard Pro',
        'price': 297.0, 'price_individual': 374.90,
        'savings': 'Economize R$ 77,90',
        'courses': 'choose_one', 'pro_months': 1
    },
    'trilha_completa': {
        'id': 'trilha_completa', 'title': 'Trilha Completa',
        'price': 1297.0, 'price_individual': 2576.0,
        'savings': 'Economize R$ 1.279',
        'courses': 'all', 'pro_months': 12
    },
    'institucional_cursos': {
        'id': 'institucional_cursos', 'title': 'Institucional + Cursos',
        'price': 1997.0, 'price_individual': 4500.0,
        'savings': 'Economize R$ 2.503',
        'courses': 'all', 'pro_months': 12
    },
}


# ========== ENDPOINTS ==========

@router.get("", response_model=List[CourseResponse])
async def list_courses():
    """Lista todos os cursos disponiveis"""
    return list(COURSES_DATA.values())


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str):
    """Detalhes de um curso"""
    if course_id not in COURSES_DATA:
        raise HTTPException(status_code=404, detail="Curso nao encontrado")
    return COURSES_DATA[course_id]


@router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_course(
    course_id: str,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Matricula o usuario em um curso"""
    if course_id not in COURSES_DATA:
        raise HTTPException(status_code=404, detail="Curso nao encontrado")

    # Em produção: salva no DB
    # Aqui: simulamos sucesso
    return {
        "course_id": course_id,
        "enrolled_at": datetime.utcnow(),
        "user_id": user.id,
        "message": f"Matriculado em {COURSES_DATA[course_id]['title']}"
    }


@router.get("/my/list", response_model=List[str])
async def my_courses(user = Depends(get_current_user)):
    """Cursos matriculados do usuario"""
    # Em produção: query no DB
    # Demo: retorna lista do localStorage via header custom (workaround)
    return []  # Sera preenchido pelo frontend via localStorage


@router.post("/{course_id}/progress")
async def save_progress(
    course_id: str,
    progress: ProgressUpdate,
    user = Depends(get_current_user)
):
    """Salva progresso do curso"""
    return {
        "course_id": course_id,
        "module_index": progress.module_index,
        "completed": progress.completed,
        "saved_at": datetime.utcnow()
    }


@router.get("/{course_id}/certificate", response_model=CertificateResponse)
async def get_certificate(
    course_id: str,
    user = Depends(get_current_user)
):
    """Emite certificado de conclusao"""
    if course_id not in COURSES_DATA:
        raise HTTPException(status_code=404, detail="Curso nao encontrado")

    course = COURSES_DATA[course_id]
    cert_id = f"AUXF-{uuid.uuid4().hex[:12].upper()}"

    return CertificateResponse(
        course_id=course_id,
        course_title=course['title'],
        user_name=user.name,
        issued_at=datetime.utcnow(),
        certificate_id=cert_id,
        hours=course['modules'] * 2,
        validation_url=f"https://auxfarmacia.com.br/verify/{cert_id}"
    )


@router.post("/bundles/{bundle_id}/purchase")
async def purchase_bundle(
    bundle_id: str,
    user = Depends(get_current_user)
):
    """Compra um bundle"""
    if bundle_id not in BUNDLES:
        raise HTTPException(status_code=404, detail="Bundle nao encontrado")

    bundle = BUNDLES[bundle_id]
    return {
        "bundle_id": bundle_id,
        "title": bundle['title'],
        "price": bundle['price'],
        "payment_id": f"pay_{uuid.uuid4().hex[:10]}",
        "pix_code": f"00020126{len(str(bundle['price'])):02d}14{str(bundle['price'])}",
        "message": "Pagamento criado. Pague o PIX para liberar."
    }