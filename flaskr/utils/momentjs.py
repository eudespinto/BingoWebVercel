from markupsafe import Markup
import datetime
from jinja2 import Environment

env = Environment(extensions=['jinja2_time.TimeExtension'])
template = env.from_string("{% now 'local' %}")
template.render()


class now():
    def clock(self):
        while True:
            # print(datetime.datetime.now().strftime("%H:%M:%S"), end="\r")
            return datetime.datetime.now()
            # time.sleep(1)

    def time(self):
        pass


class momentjs(object):

    def __init__(self, timestamp):
        # self.timestamp = now().clock()
        self.timestamp = timestamp if str(type(timestamp)) != "<class 'jinja2.runtime.Undefined'>" else now().clock()

    # Wrapper to call moment.js method
    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (
        self.timestamp.strftime("%Y-%m-%dT%H:%M:%S"), format))
        # return format

    # Format time
    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):

        # return self.render(now().clock())
        return self.render("fromNow()")
