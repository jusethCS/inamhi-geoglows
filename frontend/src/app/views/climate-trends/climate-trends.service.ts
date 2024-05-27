import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class ClimateTrendsService {

  constructor(private http:HttpClient) {
  }

  // Retrieve JWT token for user authentication
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

      console.log(url);

      return this.http.get(url);

    }
}


// # http://ec2-3-211-227-44.compute-1.amazonaws.com/api/metdata/get-metdata?product=chirps&temp=monthly&start=2023-01-01&end=2023-12-31&code=1301
