from django.db import models

# Create your models here.
class FlightData(models.Model):
    dep_arrival_times = models.CharField(max_length=255)
    airlines = models.CharField(max_length=255)
    durations_stops = models.CharField(max_length=255)
    layovers = models.CharField(max_length=255)
    prices = models.CharField(max_length=255)

    @property
    def __str__(self):
        return f"{self.dep_arrival_times} - {self.airlines} - {self.prices}"