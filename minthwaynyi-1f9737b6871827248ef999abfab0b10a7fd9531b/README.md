# Money Tracker
### Video Demo:  <https://youtu.be/EDRmwD2se-A>
## Description:
This is a web application called "Money Tracker." As the name suggests, it is designed to help people track the money they earn and spend.

In terms of account registration, login/logout and signup procedures in this application are quite traditional and intuitive.

### Features

- **Track earnings and spending.**

- **Filter Data by utilizing different parameters.**

- **Edit or delete the recorded data.**

- **Keep a record of total earnings, total spending, and the net total.**

- **Automatically calculate the monthly average earnings and spending.**

## Details about the Features

### New Entry
A button labeled 'New Entry' in the navigation bar will take you to a form where you can input the amount of money in USD, specify whether it was earned or spent, provide the reason behind the transaction, and enter the date. Additionally, you can assign a tag to the transaction; however, this input is optional, whereas the others are all required.

Once the form is submitted, the "transaction history" table—the bottom table on the home page—will be updated, with the latest entries added to the top.

### Filter
The 'Filter' option is also available in the navigation bar. Clicking on it will display a form similar to the one in 'New Entry.' However, there are slight changes, including radio buttons for limiting the amount of money (above or below a certain threshold) and two date boxes for setting up a time frame. In this form, none of the inputs are mandatory, allowing you to freely set up criteria for the results you want to filter.

For example, selecting 'Above,' '1000,' 'spending,' '01/01/2023,' and '30/06/2023' will show you transactions where you spent more than a thousand dollars in the first half of 2023. Tags can also be handy in filtering, helping to keep the data organized. If, for instance, you tag every purchase related to entertainment with the label 'entertainment,' it becomes easier to review how much you spent on entertainment during a specific period or the types of entertainment expenses you incurred.

### Edit & Delete
In the "trransaction history" table from the homepage or in the "filtered results" table, you can not only review your earnings and expenditures but also edit or delete them individually.

### Summary Tables
At the top of the home page, there is a table called 'Summary' that displays the total earnings, total spending, and the net total. Similarly, after applying filters, you can view a table with the exact same name, presenting the total earnings, total spending, and net amount of money related to the filtered results.

### Monthly Averages
Below the summary table on the home page, another table, named 'Monthly Average,' can be seen. Average monthly earnings and expenditures are automatically calculated based on the history of all transactions. This feature serves to remind users of their monthly income and spending patterns.

## Design
I tried to keep the looks of the application as clean and minimal as possible. I tried to ensure every text and button is easily visible. The overall theme leans into the darker shades in order to reduce eye strain for users.
