import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';


@Injectable({
  providedIn: 'root'
})


export class AuthService {

  // Service attributes
  private auth = false;
  private token = "";

  // Constructor
  constructor(private http:HttpClient) { }

  // Retrieve JWT token for user authentication
  get_token(email:string, password:string):Observable<any>{
    const url = environment.urlAPI + "login?user=" + email + "&pass=" + password;
    return this.http.get(url)
  }

  // Register user
  register_user(data:any):Observable<any>{
    const url = environment.urlAPI +
                  "register?email=" + data.email +
                  "&pass=" + data.pass +
                  "&firstname=" + data.firstname +
                  "&lastname=" + data.lastname +
                  "&institution=" + data.institution +
                  "&position=" + data.position
    return this.http.get(url)
  }

  // User authentication
  login(tokenData:string): void {
    this.token = tokenData;
    if(this.token !== ""){
      this.auth = true;
    }
  }

  // Finish session
  logout(): void {
    this.token = "";
    this.auth = false;
  }

  // Determine if user is authenticated
  isAuth(): boolean {
    return this.auth;
  }

}
