from fastapi import FastAPI, HTTPException, Depends
from Auth.Auth_handler import signJWT, get_password_hash, verify_password
from Auth.Auth_bearer import JWTBearer
import json

with open("tryout.json", "r") as readFile:
    daftarTryout = json.load(readFile)

with open("account.json", "r") as readUser:
    daftarUser = json.load(readUser)

app = FastAPI()

@app.post("/user/sign-up", tags = ['User'])
async def register(username: str, email : str, password: str):
    for list_user in daftarUser['user']:
        if list_user['username'] == username:
            return ({'Message' : "Username sudah digunakan!"})
        else :
            hashpassword = get_password_hash(password)
            newuser = {'username': username, 'email': email, 'password': hashpassword, 'saldo': 0, 'produk': ""}
            daftarUser['user'].append(newuser)
            with open("account.json", "w") as writeUser:
                json.dump(daftarUser, writeUser, indent = 4)
            writeUser.close()
            return ({'Message' : "User berhasil di-tambahkan."})
 
@app.post("/user/login", tags = ['User'])
async def login(email: str, password: str):
    for list_user in daftarUser['user']:
        if list_user['email'] == email:
            if verify_password(password, list_user['password']):
                return signJWT(email)
            else:
                return ({'Message' : "Password yang dimasukkan salah."})
    return ({'Message' : "Email tidak ditemukan."})

@app.put("/user/top-up", dependencies=[Depends(JWTBearer())], tags = ['Saldo'])
async def isi_saldo(password: str, Saldo: int):
    for list_user in daftarUser['user']:
        if verify_password(password, list_user['password']):
            list_user['saldo'] = list_user['saldo'] + Saldo
            readUser.close()
            with open("account.json", "w") as writeUser:
                json.dump(daftarUser, writeUser, indent = 4)
            writeUser.close()
            return({'Message' : "Saldo berhasil ditambahkan."})
    raise HTTPException(
        status_code = 500, detail =f'Wrong Credentials'
    )

@app.get("/user/ceksaldo", dependencies=[Depends(JWTBearer())], tags = ['Saldo'])
async def cek_saldo(username : str):
    for list_user in daftarUser['user']:
        if list_user['username'] == username:
            return list_user['saldo']

@app.get("/user/list_all_tryout", dependencies=[Depends(JWTBearer())], tags = ['Tryout'])
async def view_all_tryout():
    return daftarTryout

@app.get("/user/list_tryout", dependencies=[Depends(JWTBearer())], tags = ['Tryout'])
async def view_tryout(idtryout : int):
    for list_tryout in daftarTryout["tryout"]:
        if list_tryout["id_tryout"] == idtryout:
            return list_tryout
    raise HTTPException(
        status_code = 404, detail =f'Tryout not Found'
    )

@app.get("/user/tryout", dependencies=[Depends(JWTBearer())], tags = ['Tryout'])
async def view_owned_tryout(username : str):
    for list_user in daftarUser['user']:
        if list_user['username'] == username:
            return list_user['produk']

@app.put("/user/pembayaran", dependencies=[Depends(JWTBearer())], tags = ['Pembayaran'])
async def bayar_tryout(password : str, idtryout : int):
    for list_user in daftarUser['user']:
        if verify_password(password, list_user['password']):
            for list_tryout in daftarTryout['tryout']:
                if list_tryout["id_tryout"] == idtryout:
                    if list_user['saldo'] >= list_tryout['harga']:
                        list_user['saldo'] = list_user['saldo'] - list_tryout['harga']
                        if list_user['produk'] == "":
                            list_user['produk'] = list_tryout['nama']
                        else :
                            list_user['produk'] = list_user['produk'] + ', ' + list_tryout['nama']
                        readUser.close()
                        with open("account.json", "w") as writeUser:
                            json.dump(daftarUser, writeUser, indent = 4)
                        writeUser.close()
                        return({'Message' : 'Pembelian Tryout berhasil.'})
                    else:
                        return({'Message' : 'Saldo yang anda miliki kurang.'})
    raise HTTPException(
        status_code = 505, detail =f'Timeout'
    )