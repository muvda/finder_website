import requests
from bs4 import BeautifulSoup

# params for prof = %20Name1%20Name2
# This url only work with SFU professor, in the future we could extend to other as well using
MY_PROF_QUERRY_URL = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName" \
                     "=Simon%20Fraser%20University&query="
MY_PROF_URL = "https://www.ratemyprofessors.com"
OUTLINE_BASE_URL = "http://www.sfu.ca/outlines.html?"


def scrape_rating(name):
    prof_review = {'name': name}

    name_split = name.split(' ')
    suffix = ''
    for elem in name_split:
        suffix += '%20' + elem
    query_url = MY_PROF_QUERRY_URL + suffix

    # user agent spoof
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.80 Safari/537.36'}

    session = requests.Session()
    session.headers.update(headers)
    root = session.get(query_url)
    root_soup = BeautifulSoup(root.content, "html.parser")
    prof_infos = []
    print(root_soup.findAll('a', attrs={'class': 'TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx'}))
    for lists in root_soup.findAll('a', attrs={'class': 'TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx'}):
        prof_infos.append(lists['href'])
    if len(prof_infos) != 0:
        # basic logic: obtain the first link
        prof_rating_url = MY_PROF_URL + prof_infos[0]
        review = session.get(prof_rating_url)
        review_soup = BeautifulSoup(review.content, "html.parser")
        prof_review['score'] = review_soup.find("div", {"class": "RatingValue__Numerator-qw8sqy-2 liyUjw"}).text
        feedback_num = []
        # other feedback number
        for elem in review_soup.findAll("div", {"class": "FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"}):
            feedback_num.append(elem.text)
        if len(feedback_num) >= 1:
            if '%' in feedback_num[0]:
                prof_review['take_again'] = feedback_num[0]
            else:
                prof_review['difficulty'] = feedback_num[0]
        if len(feedback_num) >= 2:
            if '%' in feedback_num[1]:
                prof_review['take_again'] = feedback_num[1]
            else:
                prof_review['difficulty'] = feedback_num[1]
        # look for all tags
        feedback_tag = []
        div_tags = review_soup.find("div", {"class": "TeacherTags__TagsContainer-sc-16vmh1y-0 dbxJaW"})
        for elem in div_tags.findAll("span", {"class": "Tag-bs9vf4-0 hHOVKF"}):
            feedback_tag.append(elem.text)
        if len(feedback_tag) >= 1:
            prof_review['tags'] = feedback_tag
        prof_review['url'] = prof_rating_url
    else:
        prof_review['error'] = 'No review available'
    return prof_review


def scrape_outline_for_app(suffix):
    outline = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.80 Safari/537.36'}
    session = requests.Session()
    session.headers.update(headers)
    url = OUTLINE_BASE_URL + suffix
    root = session.get(url)
    root_soup = BeautifulSoup(root.content, "html.parser")
    header_title = root_soup.find('div', {'class': 'custom-header'})
    course_name = header_title.find('h1', {'id': 'name'}).text + header_title.find('h2', {'id': 'title'}).text
    outline['course'] = course_name
    header_time = root_soup.find('li', {'class': 'course-times'})
    if header_time is not None:
        times_list = []
        times_raw = header_time.findAll('p')
        for time in times_raw:
            times_list.append(time.text)
        outline['time'] = times_list
    head_instr = root_soup.find('ul', {'class': 'instructorBlock1'})
    instrs = []
    if head_instr is not None:
        instrs_raw = head_instr.findAll('li', {'class': 'instructor'})
        for instr in instrs_raw:
            name_raw = instr.find_all(text=True)
            name = name_raw[2].strip()
            instrs.append(name)
        outline['instructors'] = instrs
    head_prereq = root_soup.find('li', {'class': 'prereq'})
    if head_prereq is not None:
        preq_raw = head_prereq.find_all(text=True)
        preq = preq_raw[len(preq_raw) - 1].strip()
        outline['prerequisite'] = preq
    return outline
