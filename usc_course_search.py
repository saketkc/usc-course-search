#!/usr/bin/env python
"""
Command line course search for USC
"""
import re
import sys

def err(message):
    sys.stderr.write('{0}\n\n'.format(message))
    sys.exit(1)

try:
    import requests
except ImportError:
    err('Error: python-requests not found. pip install requests')

try:
    from bs4 import BeautifulSoup
    from bs4 import NavigableString, Comment
except ImportError:
    err('Error: python-bs4 not found. pip install beautifulsoup4')

__base_url__ = 'https://classes.usc.edu'
term = None

def fetcher(url):
    response = requests.get(url)
    if response.ok is not True:
        err('Error retrieving url: {0}\n'.format(url))
    return response

def search(term, courseList):
    # Visit each page, check if shortcode belongs to searchlist
    courseList.sort()
    all_courses = {}
    for course in courseList:
        url = __base_url__ + '/{0}/classes/{1}'.format(term, course.lower())
        response = fetcher(url)
        soup = BeautifulSoup(response.text)
        courses_soup = soup.find_all('a', {'class': 'courselink'})
        for cs in courses_soup:
            course_id = cs.find('strong').string.strip().replace(' ','').replace(':', '').upper()
            course_name = ''.join(unicode(child) for child in cs.children if isinstance(child, NavigableString) and not isinstance(child, Comment))
            course_name = course_name.lstrip().rstrip()
            credits = re.sub(r'\(|\)', '', cs.find('span').string)
            all_courses[course_id] = (course_name, credits)
    return all_courses

def get_input_courses(path):
    courses = []
    with open(path, 'r') as f:
        for line in f:
            course = line.split('\t')[0]
            course = course.split('(')[0].lstrip().rstrip()
            if course:
                courses.append(course)
    return courses

def get_all_department_urls(term):
    url = __base_url__ + '/' + term
    response = fetcher(url)
    soup = BeautifulSoup(response.text)
    classes = soup.find('ul', id='sortable-classes')

    # TODO This should be sortable by school, etc

    departments = {} # Format: 'shortcode': 'expansion'
    for cl in classes.find_all('li'):
        data_code = cl['data-code']
        data_title = cl['data-title']
        departments[data_code] = data_title
    return departments

def main(args):
    term = 'term-' + args[0]
    input_courses = get_input_courses(args[1])
    print 'Input Courses: ', input_courses
    departments = [courses.split(' ')[0] for courses in input_courses]
    running_courses = set(search(term, departments).keys())
    print '\n\n\n\n'
    print 'Running Courses: ', running_courses
    courses = set([x.replace(' ', '').upper() for x in input_courses])
    print '\n\n\n\n'
    print courses.intersection(running_courses)

if __name__=='__main__':
    if (len(sys.argv)<3):
        err('python <term> <courselist_file>\n'
                         'eg. python 2015-2 searchlist.csv\n\n')

    main(sys.argv[1:])

