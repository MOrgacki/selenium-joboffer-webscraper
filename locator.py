class Locator:
    #login view
    email = "[data-test='input-email']"
    password = "[data-test='input-password'"
    login_btn = "[data-test='button-login']"

    #cookies bar
    accept_cookies_btn = "[data-test='button-accept-all-in-general']"

    #tiles view list
    pagination_number = "#pagination-under-recommended-offers > div > ul > li:nth-child(6) > a"
    
    #single offer view
    apply_button = "[data-test='anchor-apply']"

    #company view
    about_company_link = "[data-test='anchor-view-company']"
    company_profile1_link = "[data-test='button-employer-link']"
    company_profile2_link = "a.ep-profile-link"
    company_profile3_link = "a.employers-MuiButtonBase-root"
    company_data1 = ".sidebar > .contact-details > div > div.text"
    company_data2 = "ep-profile-link"