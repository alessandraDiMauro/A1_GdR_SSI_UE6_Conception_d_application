

@app.get("/ticket", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur la page ticket"}
