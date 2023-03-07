from django.db import models
from django.urls import reverse
from datetime import date

# A tuple of 2-tuples
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)
# Create your models here.
class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.color} {self.name}'
    
    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})

class Finch(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    toys = models.ManyToManyField(Toy)

    def fed_for_today(self):
        return self.feeding_set.filter(date=date.today()).count() >= len(MEALS)

    # dunder str method return finch name
    def __str__(self):
        return self.name
    
    # this is used to direct to the detail view for a resource
    def get_absolute_url(self):
        return reverse('detail', kwargs={'finch_id': self.id })

# Add new Feeding model below Finch model
class Feeding(models.Model):
    date = models.DateField('feeding date')
    meal = models.CharField(
        max_length=1,
        # add the choices field
        choices = MEALS,
        # set a default value for the meal to be 'B'
        default = MEALS[0][0]
    )
    # add finch foreign key reference
    finch = models.ForeignKey(Finch, on_delete=models.CASCADE)

    def __str__(self):
        # this method is coming from django
        # produced like this: get_<name_of_field>_display()
        return f"{self.get_meal_display()} on {self.date}"
    
    # change the default sort
    class Meta:
        ordering = ['-date']