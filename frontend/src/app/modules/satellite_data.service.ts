import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SatelliteDataService {
  constructor(private http:HttpClient) {}
  get_metdata(
    product:string, frecuency:string, startDate:string,
    endDate:string, code:string ):Observable<any>{
      const url = environment.urlAPI +
                  "metdata/get-metdata" +
                  "?product=" + product +
                  "&temp=" + frecuency +
                  "&start=" + startDate +
                  "&end=" + endDate +
                  "&code=" + code;
      return this.http.get(url);
    }
}
