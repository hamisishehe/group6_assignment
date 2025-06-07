import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UserDetails } from '../models/UserModel';
import { WebsiteData } from '../models/WebsiteModels';
import { DomainData } from '../models/DomainInfo';
import { DataTable } from 'simple-datatables';

@Component({
  selector: 'app-domain',
  imports: [HttpClientModule,CommonModule,FormsModule],
  templateUrl: './domain.component.html',
  styleUrl: './domain.component.css'
})
export class DomainComponent implements OnInit {

           isOpen = false;
    isUploadOpen=false;
    isLoading: boolean = true;

  isUpdateModalOpen = false;
  selectedStudent: any = {};  // will store student info for editing


    userData : UserDetails | null = null;
    websites: WebsiteData [] = [];
    domain_info: DomainData | null = null;
    website_id : number=0;
    website_name : string = '';

    url : string='';
    name : string='';

    constructor(private http : HttpClient ){

    }


    ngOnInit() {

      setTimeout(() => {
        this.isLoading = false;
      }, 100);

      this.GetWebsites();
      this.getProfile();

    }


    getProfile() {
      const token = localStorage.getItem('token');

      if (token) {
        // Set the Authorization header with the Bearer token
        const headers = new HttpHeaders({
          Authorization: `Bearer ${token}`,
        });



        // Make the HTTP GET request to fetch the profile
        this.http
          .get<UserDetails>(`http://localhost:5000/user/profile`, {
            headers,
          }) // Use baseUrl here
          .subscribe(
            (data) => {

              this.userData = data;

              this.userData = data;


              console.log(this.userData.id);


            },
            (error) => {
              console.error('Error fetching user profile', error);
            }
          );
      } else {
        console.error('No token found');
      }
    }


GetWebsites() {
  console.log("................");

  const token = localStorage.getItem('token');

  if (token) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<WebsiteData[]>(`http://localhost:5000/websites`, { headers })
      .subscribe(
        response => {
          this.websites = response;

          this.website_id =this.websites[0]?.id;
          this.website_name = this.websites[0]?.name;
          this.GetDomain();

          console.log(".....................................................................");



        },
        error => {
          console.error('Error fetching websites:', error);
        }
      );
  } else {
    console.error('No token found. Cannot fetch websites.');
  }
}


GetDomain() {
  console.log("................");

  const token = localStorage.getItem('token');

  if (token) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<DomainData>(`http://localhost:5000/monitor/expiry/${this.website_id}`, { headers })
      .subscribe(
        response => {
          this.domain_info = response;
                   console.log("1.....................................................................");

          console.log(response);
                   console.log("1.....................................................................");

          this.initializeTable();
        },
        error => {
          console.error('Error fetching websites:', error);
        }
      );
  } else {
    console.error('No token found. Cannot fetch websites.');
  }
}



    initializeTable(): void {
      setTimeout(() => {
        let datatable = new DataTable('#search-table');
        console.log('Table initialized');
      }, 100);
    }

}
