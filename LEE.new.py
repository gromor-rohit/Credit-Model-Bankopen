# importing libraries
from flask import Flask, jsonify, request
import json
import requests
from collections import defaultdict
from datetime import datetime
from pprint import pprint
import math
app = Flask(__name__)

@app.route('/process_rfids', methods=['POST'])
def process_rfids():
    received_data = request.get_json()
    if 'RFIDs' not in received_data:
        return {"error": "RFIDs key is missing in the request"}, 400
    RFID_data_list = []
    # return (received_data)
    # print(received_data)

    if 'RFIDs' in received_data:
        for i in received_data['RFIDs']:
            url = f"https://los.glaas.co/api/application/{i}%20/camCustom?loanProductId=88"
            payload = json.dumps({"locked": False})
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuaXRlc2guaGlydmVAZ3JvbW9yLmluIiwiZXhwIjoxNzQ2NTIxOTY3LCJpYXQiOjE3MTQ5ODU5Njd9.EHd2aFxdeZndbX-GcI2E6orcafzDD-7QYDmbBCVMPQs'}

            response = requests.request("GET", url, headers=headers, data=payload)
            print(response.text)
            json_data = json.loads(response.text)
            contact = json_data['contact'][0]
            company = json_data['company'][0]
            print(contact)
            bsa = json_data.get('bsa', [{}])[0].get('details', {}).get('cashflow', {}).get('quarterly', {})

            # Age:
            def age(contact):
                from datetime import datetime
                dob = datetime.strptime(contact['dob'], '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                # print(f"Age: {age}")
                return int(age)
                print(age)


            # ===============================================================================================
            # business vintage:
            def buisness_vintage(company):
                from datetime import datetime
                doi = datetime.strptime(company['doi'], '%d/%m/%Y')
                today = datetime.today()
                years = today.year - doi.year
                months = today.month - doi.month
                # Adjust the total months if the current month is before the birth month
                if months < 0:
                    years -= 1
                    months += 12

                # Calculate the total vintage in months
                buisness_vintage = years * 12 + months
                # print(f"Buisness Vintage: {buisness_vintage}")
                return buisness_vintage


            # ===============================================================================================
            # settlement


            # count of unsecured enquiries:
            def unsecured_enquiries(contact):
                # Initialize counts
                unsecured_inquiries_count = 0
                # secured_inquiries_count = 0

                # Process the data
                details = [i['details'] for i in contact['cic'][0]['analysedCic']['enquiry_success_ratio'] if i['month'] <= 6]

                unsecured_inquiries_count = sum(
                    j['enquiry'] for detail in details for j in detail if j['product'] in ["Business Loan", "Personal Loan"])
                # secured_inquiries_count = sum(j['enquiry'] for detail in details for j in detail if j['product'] not in ["Business Loan", "Personal Loan"])

                # total_inquiries = unsecured_inquiries_count + secured_inquiries_count

                # print(f"Total Enquiries = {total_inquiries}")
                # print(f"unsecured_inquiries_count = {unsecured_inquiries_count}")
                # return total_inquiries
                return int(unsecured_inquiries_count)


            # ===============================================================================================

            def secured_enquiries(contact):
                # Initialize counts
                # unsecured_inquiries_count = 0
                secured_inquiries_count = 0

                # Process the data
                details = [i['details'] for i in contact['cic'][0]['analysedCic']['enquiry_success_ratio'] if i['month'] <= 6]

                # unsecured_inquiries_count = sum(j['enquiry'] for detail in details for j in detail if j['product'] in ["Business Loan", "Personal Loan"])
                secured_inquiries_count = sum(
                    j['enquiry'] for detail in details for j in detail if j['product'] not in ["Business Loan", "Personal Loan"])

                # total_inquiries = unsecured_inquiries_count + secured_inquiries_count

                # print(f"Total Enquiries = {total_inquiries}")
                # print(f"unsecured_inquiries_count = {unsecured_inquiries_count}")
                # return total_inquiries
                return int(secured_inquiries_count)


            # ==================================================================================================

            # count of loans:
            def unsecured_loan_count(contact):
                live_loans = [{
                    'sanctioned_date': i['sanctioned_date'],
                    'product': i['product'],
                    'outstanding_amount': i['outstanding_amount'],
                    'status': i['status'],
                    'dpd': i['dpd']} for i in contact['cic'][0]['analysedCic']['all_loans'] if
                    i['status'] == 'live' and i['product'] != 'Gold Loan' and i['product'] != 'Consumer Loan' and i[
                        'product'] != 'Credit Card']

                unsecured_loan_count = 0
                # secured_loan_count = 0
                for i in live_loans:
                    if i['product'] == "Business Loan" or i['product'] == "Personal Loan":
                        unsecured_loan_count += 1
                #     else:
                #          secured_loan_count = secured_loan_count + 1
                # total_live_loans = unsecured_loan_count + secured_loan_count
                # print(f"unsecured_loan_count:{unsecured_loan_count}")
                # print(f"total_live_loans: {unsecured_loan_count + secured_loan_count}")
                # return total_live_loans
                return unsecured_loan_count


            # ======================================================================================================

            def credit_vintage(loan_status):
                from datetime import datetime
                earliest = datetime.strptime(loan_status['earliest'], '%d/%m/%Y')
                today = datetime.today()
                years = today.year - earliest.year
                months = today.month - earliest.month
                # Adjust the total months if the current month is before the birth month
                if months < 0:
                    years -= 1
                    months += 12

                # Calculate the total vintage in months
                credit_vintage = int(years * 12 + months)
                # print(f"Buisness Vintage: {buisness_vintage}")
                return credit_vintage


            # =======================================================================================================

            def secured_loan_count(contact):
                live_loans = [{
                    'sanctioned_date': i['sanctioned_date'],
                    'product': i['product'],
                    'outstanding_amount': i['outstanding_amount'],
                    'status': i['status'],
                    'dpd': i['dpd']} for i in contact['cic'][0]['analysedCic']['all_loans'] if
                    i['status'] == 'live' and i['product'] != 'Gold Loan' and i['product'] != 'Consumer Loan' and i[
                        'product'] != 'Credit Card']

                # unsecured_loan_count = 0
                secured_loan_count = 0
                for i in live_loans:
                    if i['product'] != "Business Loan" or i['product'] != "Personal Loan":
                        secured_loan_count = secured_loan_count + 1
                return secured_loan_count


            # ===============================================================================================

            full_name = contact['firstName'] + " " + contact['lastName']

            Age = int(age(contact))

            Buisness_Vintage = buisness_vintage(company)

            cibil_score = contact['cic'][0]['analysedCic']['score']

            settlement = int(contact['cic'][0]['analysedCic']['repayment_history']['settlement'])

            unsecured_enquiries_count = int(unsecured_enquiries(contact))

            total_enquiries = int(secured_enquiries(contact)) + int(unsecured_enquiries_count)

            unsecured_loan_count = unsecured_loan_count(contact)

            secured_loan_count = secured_loan_count(contact)
            total_live_loans = unsecured_loan_count + secured_loan_count

            loan_status = contact['cic'][0]['analysedCic']['loan_status']

            current_outstanding = int(loan_status['current_outstanding'])
            past_12_months_count = int(loan_status['past_12_months_count'])
            earliest_non_cc = loan_status['earliest_non_cc']
            current_past_12_months_count = int(loan_status['current_past_12_months_count'])
            current_sanctioned = int(loan_status['current_sanctioned'])
            total_loan_count = int(loan_status['total_loan_count'])
            earliest = loan_status['earliest']
            credit_vintage = int(credit_vintage(loan_status))
            total_outstanding = int(loan_status['total_outstanding'])
            total_sanctioned = int(loan_status['total_sanctioned'])
            current_count = int(loan_status['current_count'])
            latest = loan_status['latest']


            # =============================================================================================

            # BSA details
            precisaScore = json_data['bsa'][0]['details']['summary']['precisaScore']
            volatilityScore = json_data['bsa'][0]['details']['summary']['volatilityScore']

            period_l3m = bsa[0]['month']
            inflow_l3m = float(bsa[0]['inflow'])
            outflow_l3m = float(bsa[0]['outflow'])
            adb_l3m = float(bsa[0]['avgDailyBalance'])
            inflow_txn_l3m = float(bsa[0]['inflowTransactionCount'])
            outflow_txn_l3m = float(bsa[0]['outflowTransactionCount'])


            period_l6m = bsa[1]['month']
            inflow_l6m = float(bsa[1]['inflow'])
            outflow_l6m = float(bsa[1]['outflow'])
            adb_l6m = float(bsa[1]['avgDailyBalance'])
            inflow_txn_l6m = float(bsa[1]['inflowTransactionCount'])
            outflow_txn_l6m = float(bsa[1]['outflowTransactionCount'])


            period_l12m = bsa[3]['month']
            inflow_l12m = float(bsa[3]['inflow'])
            outflow_l12m = float(bsa[3]['outflow'])
            adb_l12m = float(bsa[3]['avgDailyBalance'])
            inflow_txn_l12m = float(bsa[3]['inflowTransactionCount'])
            outflow_txn_l12m = float(bsa[3]['outflowTransactionCount'])
            average_monthly_inflow = inflow_l12m

            # =====================================================================================
            # Credit Evaluation
            class CreditAnalysisModel:
                def __init__(self, Age, Buisness_Vintage, cibil_score, settlement, unsecured_enquiries_count, total_enquiries,
                             unsecured_loan_count, total_live_loans, precisaScore, adb_l3m, adb_l6m, inflow_l12m):
                    self.Age = Age
                    self.Buisness_Vintage = Buisness_Vintage
                    self.cibil_score = int(cibil_score)
                    self.settlement = settlement
                    self.total_enquiries = total_enquiries
                    self.unsecured_enquiries_count = unsecured_enquiries_count
                    self.unsecured_loan_count = unsecured_loan_count
                    self.total_live_loans = total_live_loans
                    self.precisaScore = precisaScore
                    self.adb_l3m = adb_l3m
                    self.adb_l6m = adb_l6m
                    self.inflow_l12m = inflow_l12m
                    self.weights = {
                        'Buisness_Vintage': 0.10,
                        'cibil_score': 0.10,
                        'total_enquiries': 0.10,
                        'unsecured_enquiries_count': 0.10,
                        'unsecured_loan_count': 0.10,
                        'total_live_loans': 0.10,
                        'precisaScore': 0.10,
                        'adb_l3m': 0.10,
                        'adb_l6m': 0.10,
                        'inflow_l12m': 0.10

                    }

                def policy_check(self):
                    if not (21 <= self.Age <= 60):
                        return False
                    if not (self.Buisness_Vintage > 24):
                        return False
                    if not (self.cibil_score > 700):
                        return False
                        # if not (self.total_enquiries < 21):
                        return False
                        # if not (self.unsecured_enquiries_count < 6):
                        return False
                        # if not (self.unsecured_loan_count < 5):
                        return False
                        # if not (self.precisaScore > 500):
                        return False
                    if not (self.adb_l3m > 5000):
                        return False
                    if not (self.adb_l6m > 5000):
                        return False
                    if not (self.inflow_l12m > 1500000):
                        return False
                    return True

                def calculate_weighted_score(self, value, score_map, weight):
                    for condition, score in score_map.items():
                        if condition(value):
                            return score * weight
                    return 0

                def calculate_total_weighted_score(self):
                    business_vintage_score_map = {
                        lambda x: 24 <= x <= 30: 1,
                        lambda x: 31 <= x <= 37: 2,
                        lambda x: 38 <= x <= 44: 3,
                        lambda x: 45 <= x <= 51: 4,
                        lambda x: 52 <= x <= 58: 5,
                        lambda x: 59 <= x <= 65: 6,
                        lambda x: 66 <= x <= 72: 7,
                        lambda x: 73 <= x <= 79: 8,
                        lambda x: 80 <= x <= 86: 9,
                        lambda x: x > 87: 10
                    }

                    bureau_score_map = {
                        lambda x: 725 <= x <= 740: 1,
                        lambda x: 741 <= x <= 756: 2,
                        lambda x: 757 <= x <= 772: 3,
                        lambda x: 773 <= x <= 788: 4,
                        lambda x: 789 <= x <= 804: 5,
                        lambda x: 805 <= x <= 820: 6,
                        lambda x: 821 <= x <= 836: 7,
                        lambda x: 837 <= x <= 852: 8,
                        lambda x: 853 <= x <= 868: 9,
                        lambda x: x > 869: 10
                    }

                    total_enquiries_map = {
                        lambda x: x in [29, 30, 31]: -5,
                        lambda x: x in [26, 27, 28]: -4,
                        lambda x: x in [23, 24, 25]: -3,
                        lambda x: x in [21, 22]: -2,
                        lambda x: x in [19, 20]: -1,
                        lambda x: x in [17, 18]: 0,

                        lambda x: x == 16: 1,
                        lambda x: x == 15: 2,
                        lambda x: x == 14: 3,
                        lambda x: 12 <= x <= 13: 4,
                        lambda x: 10 <= x <= 11: 5,
                        lambda x: 8 <= x <= 9: 6,
                        lambda x: 6 <= x <= 7: 7,
                        lambda x: 4 <= x <= 5: 8,
                        lambda x: 2 <= x <= 3: 9,
                        lambda x: 0 <= x <= 1: 10
                    }

                    unsecured_enquiries_count_map = {
                        lambda x: x in [23, 24, 25]: -5,
                        lambda x: x in [20, 21, 22]: -4,
                        lambda x: x in [17, 18, 19]: -3,
                        lambda x: x in [15, 16]: -2,
                        lambda x: x in [13, 14]: -1,
                        lambda x: x in [11, 12]: 0,

                        lambda x: x in [9, 10]: 1,
                        lambda x: x == 8: 2,
                        lambda x: x == 7: 3,
                        lambda x: x == 6: 4,
                        lambda x: x == 5: 5,
                        lambda x: x == 4: 6,
                        lambda x: x == 3: 7,
                        lambda x: x == 2: 8,
                        lambda x: x == 1: 9,
                        lambda x: x == 0: 10
                    }

                    unsecured_loan_count_map = {

                        lambda x: x in [13, 14]: -4,
                        lambda x: x in [11, 12]: -3,
                        lambda x: x in [9, 10]: -2,
                        lambda x: x in [7, 8]: -1,
                        lambda x: x in [5, 6]: 0,

                        lambda x: x == 4: 1,
                        lambda x: x == 3: 2,
                        lambda x: x == 2: 3,
                        lambda x: x == 1: 4,
                        lambda x: x == 0: 5,

                    }

                    total_live_loans_map = {
                        lambda x: x in [18, 19]: -4,
                        lambda x: x in [16, 17]: -3,
                        lambda x: x in [14, 15]: -2,
                        lambda x: x in [12, 13]: -1,
                        lambda x: x in [10, 11]: 0,

                        lambda x: x == 9: 1,
                        lambda x: x == 8: 2,
                        lambda x: x == 7: 3,
                        lambda x: x == 6: 4,
                        lambda x: x == 5: 5,
                        lambda x: x == 4: 6,
                        lambda x: x == 3: 7,
                        lambda x: x == 2: 8,
                        lambda x: x == 1: 9,
                        lambda x: x == 0: 10

                    }

                    precisaScore_map = {
                        lambda x: 500 <= x <= 540: 1,
                        lambda x: 541 <= x <= 580: 2,
                        lambda x: 581 <= x <= 620: 3,
                        lambda x: 621 <= x <= 661: 4,
                        lambda x: 662 <= x <= 702: 5,
                        lambda x: 703 <= x <= 743: 6,
                        lambda x: 744 <= x <= 784: 7,
                        lambda x: 785 <= x <= 825: 8,
                        lambda x: 826 <= x <= 866: 9,
                        lambda x: x > 867: 10

                    }

                    adb_l3m_map = {
                        lambda x: 7500 <= x <= 8000: -4,
                        lambda x: 8001 <= x <= 8500: -3,
                        lambda x: 8501 <= x <= 9000: -2,
                        lambda x: 9001 <= x <= 9500: -1,
                        lambda x: 9501 <= x <= 9999: 0,

                        lambda x: 10000 <= x <= 30000: 1,
                        lambda x: 30001 <= x <= 55000: 2,
                        lambda x: 55001 <= x <= 80000: 3,
                        lambda x: 80001 <= x <= 105000: 4,
                        lambda x: 105001 <= x <= 130000: 5,
                        lambda x: 130001 <= x <= 155000: 6,
                        lambda x: 155001 <= x <= 180000: 7,
                        lambda x: 180001 <= x <= 205000: 8,
                        lambda x: 205001 <= x <= 230000: 9,
                        lambda x: x > 230001: 10

                    }

                    adb_l6m_map = {
                        lambda x: 7500 <= x <= 8000: -4,
                        lambda x: 8001 <= x <= 8500: -3,
                        lambda x: 8501 <= x <= 9000: -2,
                        lambda x: 9001 <= x <= 9500: -1,
                        lambda x: 9501 <= x <= 9999: 0,

                        lambda x: 10000 <= x <= 30000: 1,
                        lambda x: 30001 <= x <= 55000: 2,
                        lambda x: 55001 <= x <= 80000: 3,
                        lambda x: 80001 <= x <= 105000: 4,
                        lambda x: 105001 <= x <= 130000: 5,
                        lambda x: 130001 <= x <= 155000: 6,
                        lambda x: 155001 <= x <= 180000: 7,
                        lambda x: 180001 <= x <= 205000: 8,
                        lambda x: 205001 <= x <= 230000: 9,
                        lambda x: x > 230001: 10

                    }

                    inflow_l12m_map = {
                        lambda x: 1500000 <= x <= 3000000: 1,
                        lambda x: 3000001 <= x <= 4500000: 2,
                        lambda x: 4500001 <= x <= 6000000: 3,
                        lambda x: 6000001 <= x <= 7500000: 4,
                        lambda x: 7500001 <= x <= 9000000: 5,
                        lambda x: 9000001 <= x <= 10500000: 6,
                        lambda x: 10500001 <= x <= 12000000: 7,
                        lambda x: 12000001 <= x <= 13500000: 8,
                        lambda x: 13500001 <= x <= 15000000: 9,
                        lambda x: x > 15000001: 10

                    }

                    # total_weighted_score = 0
                    TWS_Buisness_Vintage = self.calculate_weighted_score(self.Buisness_Vintage, business_vintage_score_map,
                                                                         self.weights['Buisness_Vintage'])
                    TWS_cibil_score = self.calculate_weighted_score(self.cibil_score, bureau_score_map, self.weights['cibil_score'])
                    TWS_total_enquiries = self.calculate_weighted_score(self.total_enquiries, total_enquiries_map,
                                                                        self.weights['total_enquiries'])
                    TWS_unsecured_enquiries_count = self.calculate_weighted_score(self.unsecured_enquiries_count,
                                                                                  unsecured_enquiries_count_map,
                                                                                  self.weights['unsecured_enquiries_count'])
                    TWS_unsecured_loan_count = self.calculate_weighted_score(self.unsecured_loan_count, unsecured_loan_count_map,
                                                                             self.weights['unsecured_loan_count'])
                    TWS_total_live_loans = self.calculate_weighted_score(self.total_live_loans, total_live_loans_map,
                                                                         self.weights['total_live_loans'])
                    TWS_precisaScore = self.calculate_weighted_score(self.precisaScore, precisaScore_map,
                                                                     self.weights['precisaScore'])
                    TWS_adb_l3m = self.calculate_weighted_score(self.adb_l3m, adb_l3m_map, self.weights['adb_l3m'])
                    TWS_adb_l6m = self.calculate_weighted_score(self.adb_l6m, adb_l6m_map, self.weights['adb_l6m'])
                    TWS_inflow_l12m = self.calculate_weighted_score(self.inflow_l12m, inflow_l12m_map, self.weights['inflow_l12m'])

                    total_weighted_score = TWS_Buisness_Vintage + TWS_cibil_score + TWS_total_enquiries + TWS_unsecured_enquiries_count + TWS_unsecured_loan_count + TWS_total_live_loans + TWS_precisaScore + TWS_adb_l3m + TWS_adb_l6m + TWS_inflow_l12m

                    return total_weighted_score

                def calculate_risk_score(self, total_weighted_score):
                    max_possible_score = sum(self.weights.values()) * 10
                    risk_score = (total_weighted_score / max_possible_score) * 100
                    return risk_score

                def determine_multiplier(self, risk_score):
                    if risk_score < 25:
                        return 0  # Reject application
                    elif 26 <= risk_score <= 40:
                        return 0.75
                    elif 41 <= risk_score <= 55:
                        return 1
                    elif 56 <= risk_score <= 70:
                        return 1.25
                    else:
                        return 1.5

                def calculate_loan_amount(self, multiplier):
                    return (self.inflow_l12m/12) * multiplier

                def evaluate_application(self):
                    if not self.policy_check():
                        return "Application Rejected due to policy check failure"

                    total_weighted_score = self.calculate_total_weighted_score()
                    risk_score = self.calculate_risk_score(total_weighted_score)
                    multiplier = self.determine_multiplier(risk_score)

                    if multiplier == 0:
                        return "Application Rejected due to high risk score"

                    loan_amount = self.calculate_loan_amount(multiplier)
                    # return f"Application Approved with Loan Amount: {loan_amount} and Risk Score: {risk_score:.2f}% and Multiplier: {multiplier}"
                    LEE_dict = {"Approved Loan Amount": math.floor(loan_amount / 10000) * 10000,
                                "Risk Score": round(risk_score),
                                "Multiplier": multiplier,
                                "weighted Score": total_weighted_score
                                }
                    return LEE_dict



            applicant = CreditAnalysisModel(Age, Buisness_Vintage, cibil_score, settlement, unsecured_enquiries_count, total_enquiries,
                             unsecured_loan_count, total_live_loans, precisaScore, adb_l3m, adb_l6m, inflow_l12m)


            # ============================================================================================================
            # getting json output

            json_output = {"applicant": {"Full Name": full_name,
                                  "Age": Age,
                                  "Buisness_Vintage": Buisness_Vintage},

                    "Bureau Details": {"cibil_score": cibil_score,
                                       "Settlements in L24M": settlement,
                                       "Total number of unsecured enquiries in Last 6 months": unsecured_enquiries_count,
                                       "Total number of enquiries in last 6 months": total_enquiries,
                                       "Total Unsecured Loan Count": unsecured_loan_count,
                                       "Total Live loans": total_live_loans,
                                       "current_outstanding": current_outstanding,
                                       "past_12_months_count": past_12_months_count,
                                       "earliest_non_cc": earliest_non_cc,
                                       "current_past_12_months_count": current_past_12_months_count,
                                       "current_sanctioned": current_sanctioned,
                                       "total_loan_count": total_loan_count,
                                       "earliest": earliest,
                                       "credit_vintage": credit_vintage,
                                       "total_outstanding": total_outstanding,
                                       "total_sanctioned": total_sanctioned,
                                       "current_count": current_count,
                                       "latest": latest},

                    "BSA Details": {"BSA Score": precisaScore,
                                    "Volatility Score": volatilityScore,
                                    "Last 3 Months": {"Period": period_l3m,
                                                      "inflow": inflow_l3m,
                                                      "outflow": outflow_l3m,
                                                      "ABB": adb_l3m,
                                                      "inflow_txn": inflow_txn_l3m,
                                                      "outflow_txn": outflow_txn_l3m},

                                    "Last 6 Months":
                                        {"Period": period_l6m,
                                         "inflow": inflow_l6m,
                                         "outflow": outflow_l6m,
                                         "ABB": adb_l6m,
                                         "inflow_txn": inflow_txn_l6m,
                                         "outflow_txn": outflow_txn_l6m},

                                    "Last 12 Months":
                                        {"Period": period_l12m,
                                         "inflow": inflow_l12m,
                                         "outflow": outflow_l12m,
                                         "ABB": adb_l12m,
                                         "inflow_txn": inflow_txn_l12m,
                                         "outflow_txn": outflow_txn_l12m}},

                    "Credit Evaluation": (applicant.evaluate_application())

                    }
            return jsonify(json_output)


if __name__ == '__main__':
     app.run(debug=True)