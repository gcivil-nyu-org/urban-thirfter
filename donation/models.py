from django.db import models
from django.utils import timezone
from django import forms

#from django.contrib.auth.models import User
# Import reverse
from django.urls import reverse
from PIL import Image
from django.contrib.auth.models import User
from places.fields import PlacesField

# Create your models here.
class _Image(Image.Image):

    def crop_to_aspect(self, aspect, divisor=1, alignx=0.5, aligny=0.5):
        """Crops an image to a given aspect ratio.
        Args:
            aspect (float): The desired aspect ratio.
            divisor (float): Optional divisor. Allows passing in (w, h) pair as the first two arguments.
            alignx (float): Horizontal crop alignment from 0 (left) to 1 (right)
            aligny (float): Vertical crop alignment from 0 (left) to 1 (right)
        Returns:
            Image: The cropped Image object.
        """
        if self.width / self.height > aspect / divisor:
            newwidth = int(self.height * (aspect / divisor))
            newheight = self.height
        else:
            newwidth = self.width
            newheight = int(self.width / (aspect / divisor))
        img = self.crop((alignx * (self.width - newwidth),
                         aligny * (self.height - newheight),
                         alignx * (self.width - newwidth) + newwidth,
                         aligny * (self.height - newheight) + newheight))
        return img

Image.Image.crop_to_aspect = _Image.crop_to_aspect

##################### SQL Query #####################
# BEGIN;
# --
# -- Create model ResourcePost
# --
# CREATE TABLE "donation_resourcepost" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(100) NOT NULL, "description" text NOT NULL, "quantity" integer NOT NULL, "dropoff_time_1" datetime NOT NULL, "dropoff_time_2" datetime NOT NULL, "dropoff_time_3" datetime NOT NULL, "date_created" datetime NOT NULL, "dropoff_location" text NOT NULL, "resource_category" varchar(100) NOT NULL, "status" varchar(100) NOT NULL);
# COMMIT;
##################### SQL Query #####################

# User Models save database specifically for USERS
RESROUCE_CATEGORY_CHOICES = (
    ('FOOD', 'Food'), 
    ('MDCL','Medical/ PPE'), 
    ('CLTH','Clothing/ Covers'),
    ('ELEC','Electronics'),
    ('OTHR','Others')
)
STATUS_CHOICES = (
    ('AVAILABLE', 'Available'),
    ('PENDING', 'Pending'),
    ('NOTAVAILABLE', 'Not Available'),
)
class ResourcePost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.IntegerField()
    #dropoff_time_1 = forms.DateTimeField(widget=DateTimePicker(options={'format': '%Y-%m-%d %H:%M','language': 'en-us'}))
    dropoff_time_1 = models.DateTimeField(default=timezone.now)
    dropoff_time_2 = models.DateTimeField(blank=True,null=True)
    dropoff_time_3 = models.DateTimeField(blank=True,null=True)
    date_created = models.DateTimeField(default = timezone.now)
    # donor_id = models.ForeignKey(User, on_delete=models.CASCADE) # 1:n relationship
    dropoff_location = PlacesField(blank=True,null=True)
    #dropoff_geolocation = 
    resource_category = models.CharField(max_length=100,choices=RESROUCE_CATEGORY_CHOICES)
    image = models.ImageField(default ='donation-pics/default.jpg', upload_to='donation-pics',blank=True)
    status = models.CharField(max_length=100, choices = STATUS_CHOICES, default='Available')
    
    # Dunder (abbr. for Double Under)/Magic str method define how the object is printed
    def __str__(self):
        return self.title
    
    # Reverse would return the full url as a string and let the view redirect for us
    def get_absolute_url(self):
        # return the path of the specific post
        return reverse('donation-detail', kwargs={'pk': self.pk})
    
    def save(self):
        super().save()

        path = self.image.path
        img = Image.open(path)
        
        #2. resize the image to 300,300 if larger
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img = img.crop_to_aspect(300,300)
            img.thumbnail(output_size)
            img.save(path)