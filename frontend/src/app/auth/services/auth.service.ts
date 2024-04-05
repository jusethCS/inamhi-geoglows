import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';


@Injectable({
  providedIn: 'root'
})

export class AuthService {

  private auth = false;
  private token = "";

  constructor(private http:HttpClient) { }


  get_token(email:string, password:string):Observable<any>{
    return this.http.get( environment.urlAPI + "login?user=" + email + "&pass=" + password)
  }

  login(tokenData:string) {
    this.token = tokenData;
    if(this.token !== ""){
      this.auth = true;
    }
  }

  logout() {
    this.token = "";
    this.auth = false;
  }

  isAuth(): boolean {
    return this.auth;
  }

}
