#!/usr/bin/env python
# coding: utf-8

# In[8]:


from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd


# In[2]:


# code resource: Ömer Sakarya (https://github.com/arapfaik/scraping-glassdoor-selenium)

def get_jobs(num_jobs, verbose):
    
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()
    
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    #options.add_argument('headless')
    
    #Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path="C:/Users/Diwaker Rathore/Downloads/chromedriver_win32/chromedriver", options=options)
    driver.set_window_size(1120, 1000)

    url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=&locT=N&locId=115&jobType=&context=Jobs&sc.keyword=data+scientist&dropdown=0"
    driver.get(url)
    jobs = []

    while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.

        #Let the page load. Change this number based on your internet speed.
        #Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(10)

        #Test for the "Sign Up" prompt and get rid of it.
        try:
            driver.find_element_by_class_name("selected").click()
        except ElementClickInterceptedException:
            pass

        time.sleep(1)

        try:
            driver.find_element_by_css_selector('[alt="Close"]').click()  #clicking to the X.
        except NoSuchElementException:
            pass


        
        #Going through each job in this page
        job_buttons = driver.find_elements_by_class_name("jl")  #jl for Job Listing. These are the buttons we're going to click.
        for job_button in job_buttons:  

            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break

            job_button.click()  #You might 
            time.sleep(5)
            collected_successfully = False
            
            while not collected_successfully:
                try:
                    company_name = driver.find_element_by_xpath('.//div[@class="employerName"]').text
                    location = driver.find_element_by_xpath('.//div[@class="location"]').text
                    job_title = driver.find_element_by_xpath('.//div[contains(@class, "title")]').text
                    job_description = driver.find_element_by_xpath('.//div[@class="jobDescriptionContent desc"]').text
                    collected_successfully = True
                except:
                    time.sleep(10)

            try:
                salary_estimate = driver.find_element_by_xpath('.//span[@class="css-1uyte9r css-hca4ks e1wijj242"]').text
            except NoSuchElementException:
                salary_estimate = -1 #You need to set a "not found value. It's important."
            
            try:
                rating = driver.find_element_by_xpath('.//span[@class="rating"]').text
            except NoSuchElementException:
                rating = -1 #You need to set a "not found value. It's important."

            #Printing for debugging
            if verbose:
                print("Job Title: {}".format(job_title))
                print("Salary Estimate: {}".format(salary_estimate))
                print("Job Description: {}".format(job_description[:500]))
                print("Rating: {}".format(rating))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))

            #Going to the Company tab...
            #clicking on this:
            #<div class="tab" data-tab-type="overview"><span>Company</span></div>
            try:
                driver.find_element_by_xpath('.//div[@class="tab" and @data-tab-type="overview"]').click()

                try:
                    size = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Size"]//following-sibling::*').text
                except NoSuchElementException:
                    size = -1

                try:
                    industry = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Industry"]//following-sibling::*').text
                except NoSuchElementException:
                    industry = -1

                try:
                    sector = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Sector"]//following-sibling::*').text
                except NoSuchElementException:
                    sector = -1

                try:
                    revenue = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Revenue"]//following-sibling::*').text
                except NoSuchElementException:
                    revenue = -1

            except NoSuchElementException:  #Rarely, some job postings do not have the "Company" tab.
                headquarters = -1
                size = -1
                industry = -1
                sector = -1
                revenue = -1

                
            if verbose:
                print("Size: {}".format(size))
                print("Industry: {}".format(industry))
                print("Sector: {}".format(sector))
                print("Revenue: {}".format(revenue))
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"Job Title" : job_title,
            "Salary Estimate" : salary_estimate,
            "Job Description" : job_description,
            "Rating" : rating,
            "Company Name" : company_name,
            "Location" : location,
            "Size" : size,
            "Industry" : industry,
            "Sector" : sector,
            "Revenue" : revenue})
            #add job to jobs

        #Clicking on the "next page" button
        try:
            driver.find_element_by_xpath('.//li[@class="next"]//a').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break

    return pd.DataFrame(jobs)  #This line converts the dictionary object into a pandas DataFrame.


# In[4]:


data_final = get_jobs(200, False)
data_final


# In[5]:


data_final.to_csv('glassdoor_jobs.csv', index = False)


# In[9]:


data = pd.read_csv('glassdoor_jobs.csv')
data


# In[10]:


data.columns


# In[11]:


data['Salary Estimate'].unique()


# In[12]:


data = data[data['Salary Estimate'] != '-1']
data


# In[13]:


salary = data['Salary Estimate'].apply(lambda x: x.split(" (")[0])
salary = salary.apply(lambda x: x.replace('K','').replace('₹','').replace(',',''))


# In[14]:


salary.unique()


# In[15]:


salary = salary.apply(lambda x: x.split(' - '))
salary


# In[16]:


average_salary = []
for i in salary:
    if i[0] == '144':
        average_salary.append(144)
    elif i[0] == '600':
        average_salary.append(600)
    else:
        avg_sal = (int(i[0]) + int(i[1]))/2
        average_salary.append(avg_sal)
average_salary


# In[17]:


data['average_salary'] = average_salary
data


# In[18]:


data['company'] = data['Company Name'].apply(lambda x: x.split("\n")[0])
data


# In[19]:


data['Location'].unique()


# In[20]:


data['python'] = data['Job Description'].apply(lambda x: 1 if 'python' in x.lower() else 0)
data['spark'] = data['Job Description'].apply(lambda x: 1 if 'spark' in x.lower() else 0)
data['sql'] = data['Job Description'].apply(lambda x: 1 if 'sql' in x.lower() else 0)
data['ms_excel'] = data['Job Description'].apply(lambda x: 1 if 'excel' in x.lower() else 0)
data['tableau'] = data['Job Description'].apply(lambda x: 1 if 'python' in x.lower() else 0)
data['aws'] = data['Job Description'].apply(lambda x: 1 if 'aws' in x.lower() else 0)


# In[21]:


data


# In[22]:


data.to_csv('glassdoor_jobs_cleaned.csv', index = False)


# In[23]:


dataset = pd.read_csv('glassdoor_jobs_cleaned.csv')
dataset.head()


# In[73]:


tools = ['python', 'excel', 'sas', 'spark', 'bigml', 'java', 'ruby', 'pearl', 'matlab', 'tableau', 'ms access', 'sql', 'hadoop', 'hive', 'qlikview', 'power bi', 'google analytics', 'rstudio', 'julia', 'spss', 'c++', 'nosql','']
softwares = []
for desc in dataset['Job Description']:
    software = []
    for tool in tools:
        if tool in desc.lower():
            software.append(tool)
    softwares.append(software)
for job in softwares:
    if job == ['']:
        job.append('others')
softwares


# In[75]:


dataset['tools_required'] = softwares
dataset.head()


# In[76]:


import matplotlib.pyplot as plt
import seaborn as sbn
get_ipython().run_line_magic('matplotlib', 'inline')


# In[77]:


sns.set_style("darkgrid")


# In[78]:


dataset.columns


# In[79]:


dataset['Job Title'].unique()


# In[33]:


def title_job(title):
    if 'data scientist' in title.lower():
        return 'data scientist'
    elif 'engineer' in title.lower():
        return 'data engineer'
    elif 'machine learning' in title.lower():
        return 'MLE'
    elif 'analyst' in title.lower() or 'analytics' in title.lower():
        return 'analyst'
    elif 'manager' in title.lower():
        return 'manager'
    else:
        return 'na'
    
def seniority(title):
    if 'sr' in title.lower() or 'senior' in title.lower() or 'lead' in title.lower() or 'principal' in title.lower():
        return 'senior'
    elif 'jr' in title.lower() or 'junior' in title.lower():
        return 'junior'
    else:
        return 'na'


# In[80]:


dataset['job_title_simp'] = dataset['Job Title'].apply(title_job)
dataset.job_title_simp.value_counts()


# In[81]:


dataset['seniority'] = dataset['Job Title'].apply(seniority)
dataset.seniority.value_counts()


# In[82]:


dataset.describe()


# In[83]:


dataset.to_csv('glassdoor_data_cleaned.csv', index = False)


# In[86]:


df = pd.read_csv('glassdoor_data_cleaned.csv')
df.head()


# In[87]:


df.columns


# In[88]:


df.Rating.hist()


# In[89]:


df.average_salary.hist()


# In[92]:


df.boxplot(column = ['average_salary'])


# In[91]:


df.boxplot(column = ['Rating'])


# In[97]:


df[['average_salary', 'Rating']].corr()


# In[98]:


seniority_counts = df.seniority.value_counts()
seniority_counts


# In[99]:


plt.figure(figsize = (15,8))
plt.title('Seniority')
plt.pie(seniority_counts, labels = seniority_counts.index, autopct='%1.1f%%', startangle=180)


# In[100]:


job_title_counts = df.job_title_simp.value_counts()
job_title_counts


# In[101]:


plt.figure(figsize = (15,8))
plt.title('Job titles')
plt.pie(job_title_counts, labels = job_title_counts.index, autopct='%1.1f%%', startangle=180)


# In[104]:


tools_counts = df.tools_required.value_counts()
tools_counts.unique


# ## Model building: yet to be done (will be updating soon)

# ### Resources:

# 1- Ken Jee Youtube (https://www.youtube.com/channel/UCiT9RITQ9PW6BhXK0y2jaeg)

# 2- Glassdoor scraper code resource: Ömer Sakarya (https://github.com/arapfaik/scraping-glassdoor-selenium)
