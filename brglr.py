import cv2
import gtk
import os
import twilio
import twilio.rest
from imgurpython import ImgurClient
from time import sleep

class Brglr(object):
    def __init__(self):
        self.create_start_layout()
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_ACCOUNT_SID')
        self.client = twilio.rest.TwilioRestClient(self.account_sid, self.auth_token)
        self.test_no = 'your verified number'
        self.threshold = 3000000.0
        self.imgur_client = ImgurClient(os.environ.get('IMGUR_CLIENT_ID'), 
            os.environ.get('IMGUR_CLIENT_SECRET'))
                
    def create_start_layout(self):
        # Let's create a layout using GTK!
        # Or let's not...
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Brglr")
        self.window.set_size_request(300, 150)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.fixed = gtk.Fixed()
        self.window.add(self.fixed)
        self.window.connect('destroy', gtk.main_quit)
        
        self.no_field = gtk.Entry()
        self.no_field.set_activates_default(True)
        ok_button = gtk.Button("Okay!")
        ok_button.connect("clicked", self.handle_button, self.no_field)
        
        self.fixed.put(self.no_field, 50, 0)
        self.fixed.put(ok_button, 0, 50)
        
        self.window.show_all()

    def handle_button(self, widget, text_field):
        self.window.destroy()
        # This is currently broken, so you have to use
        # a hardcoded number
        self.number = text_field.get_text()
        print self.number
        self.start_detector()

    def imageDiff(self, prevf, currentf, nextf):
        # Get difference betwen current, prev, next then bitwise and
        d_1 = cv2.absdiff(currentf, prevf)
        d_2 = cv2.absdiff(currentf, nextf)
        return cv2.bitwise_and(d_1, d_2)

    def start_detector(self):
        self.win_name = "Brglr"
        self.cam = cv2.VideoCapture(0)
        cv2.namedWindow(self.win_name, cv2.WINDOW_AUTOSIZE)
       
        # Let light stabalize maybe?
        for i in xrange(24):
            self.cam.read()[1]

        # Read in 3 images
        # Convert to grayscale
        prevf = cv2.cvtColor(self.cam.read()[1], cv2.COLOR_RGB2GRAY)
        self.current_f_rgb = self.cam.read()[1]
        currentf = cv2.cvtColor(self.current_f_rgb, cv2.COLOR_RGB2GRAY)
        next_f_rgb = self.cam.read()[1]
        nextf = cv2.cvtColor(next_f_rgb, cv2.COLOR_RGB2GRAY)

        while True:
            # Check for ESC and destroy
            key = cv2.waitKey(10)
            if key == 27:
                cv2.destroyWindow(self.win_name)
                break

            self.current_image = self.imageDiff(prevf, currentf, nextf)            
            cv2.imshow(self.win_name, self.current_f_rgb)

            detected = self.check_motion()

            if detected == True:
                while True:
                    im = self.cam.read()[1]
                    cv2.imshow(self.win_name, im)

            # Move images along
            self.current_f_rgb = next_f_rgb
            prevf = currentf
            currentf = nextf
            nextf = cv2.cvtColor(self.cam.read()[1], cv2.COLOR_RGB2GRAY)

    def check_motion(self):
        pixel_sum, _, _, _ = cv2.sumElems(self.current_image)
        #print pixel_sum
        if (pixel_sum > self.threshold):
            sleep(1.0)
            self.current_f_rgb = self.cam.read()[1]
            cv2.imwrite('image.png', self.current_f_rgb)
            imgur_img = self.imgur_client.upload_from_path('image.png')
            link = imgur_img['link']
            body_text = "INTRUDER! " + link
            message = self.client.messages.create(body=body_text,
                    to=self.test_no,
                    from_="your twilio number")

            return True
        else:
            return False

Brglr()
gtk.main()
