from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
import uuid
from typing import List, Optional

app = FastAPI(title="API Buku Individu")

# ========================================
# 1. SKEMA DATA (Pydantic)
# Skema Input beda dengan Output (Syarat DoD #3)
# ========================================
class BukuCreate(BaseModel):
    judul: str
    # Validasi khusus Topik 1
    isbn: str = Field(..., min_length=13, max_length=13, description="ISBN harus 13 digit")
    tahun_terbit: int = Field(..., ge=1900, le=2026, description="Tahun terbit antara 1900 - 2026")

class BukuResponse(BukuCreate):
    id: str  # ID dibuat oleh server

# ========================================
# 2. DUMMY DATABASE (List di memori)
# ========================================
db_buku = []

# ========================================
# 3. ENDPOINTS
# ========================================

# POST /api/buku -> Status 201 + Header Location (Syarat DoD #2)
@app.post("/api/buku", status_code=201, response_model=BukuResponse)
def create_buku(buku: BukuCreate, response: Response):
    # Validasi 422 otomatis ditangani oleh FastAPI & Pydantic jika input salah
    
    buku_baru = BukuResponse(
        id=str(uuid.uuid4()), 
        judul=buku.judul,
        isbn=buku.isbn,
        tahun_terbit=buku.tahun_terbit
    )
    db_buku.append(buku_baru)
    
    # Tambahkan header Location
    response.headers["Location"] = f"/api/buku/{buku_baru.id}"
    return buku_baru

# GET /api/buku -> Dukung skip, limit, search (Syarat DoD #2)
@app.get("/api/buku", response_model=List[BukuResponse])
def get_semua_buku(skip: int = 0, limit: int = 10, search: Optional[str] = None):
    hasil = db_buku
    if search:
        # Filter pencarian berdasarkan judul (case-insensitive)
        hasil = [b for b in hasil if search.lower() in b.judul.lower()]
    
    # Terapkan pagination (skip & limit)
    return hasil[skip : skip + limit]

# GET /api/buku/{id} -> Status 404 jika tidak ada (Syarat DoD #2)
@app.get("/api/buku/{buku_id}", response_model=BukuResponse)
def get_buku_by_id(buku_id: str):
    for b in db_buku:
        if b.id == buku_id:
            return b
    raise HTTPException(status_code=404, detail="Buku tidak ditemukan")