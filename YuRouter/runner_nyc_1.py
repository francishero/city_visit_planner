import datetime
import os

import Yusi
from Yusi.YuRouter.prototype_parameters import PrototypeParameters
from Yusi.YuPoint.city_visit import DayVisitParameters
from Yusi.YuPoint.read_csv import ReadCSVToDict
from Yusi.YuPoint.point import Coordinates


def _GetPointsKeys():
  test_points_filepath = os.path.join(
      Yusi.GetYusiDir(), 'YuRouter', 'test_points_nyc.txt')
  lines = open(test_points_filepath).readlines()
  lines = [line.strip() for line in lines]
  keys = [line for line in lines if line and not line.startswith('#')]
  return keys


def GetPointsInput():
  points = ReadCSVToDict(
      os.path.join(Yusi.GetYusiDir(), 'YuPoint', 'test_nyc_1.csv'))
  keys = _GetPointsKeys()
  return [points[key] for key in keys]


def GetDayVisitParameterss():
  # 746 Ninth Ave, New York, NY 10019.
  house_coordinates = Coordinates(40.763582, -73.988470)
  def GetDayVisitParameters(start_datetime, end_datetime):
    return DayVisitParameters(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        lunch_start_datetime=datetime.datetime(
            start_datetime.year, start_datetime.month, start_datetime.day,
            14, 0, 0),
        lunch_hours=1.,
        start_coordinates=house_coordinates,
        end_coordinates=house_coordinates)

  return [
      GetDayVisitParameters(
          start_datetime=datetime.datetime(2015, 7, day, 11, 0, 0),
          end_datetime=datetime.datetime(2015, 7, day, 19, 0, 0))
      for day in range(13, 16)]


class CityVisitRouterRunner(object):
  
  def __init__(self):
    self.max_walking_distance=1.0
    self.city_visit_router = (
        PrototypeParameters(max_walking_distance=self.max_walking_distance,
                            validate_max_walking_distance=False).
        CityVisitRouter())

  def Run(self, points_input, day_visit_parameterss):
    return self.city_visit_router.RouteCityVisit(
        points_input, day_visit_parameterss)


def main():
  start = datetime.datetime.now()
  
  points_input = GetPointsInput()
  day_visit_parameterss = GetDayVisitParameterss()
  city_visit_router_runner = CityVisitRouterRunner()
  city_visit_best, points_left = city_visit_router_runner.Run(
      points_input, day_visit_parameterss)

  print('Points to visit in priority: %s' %
        ', '.join(point.name for point in points_input))
  print('Maximum walking distance: %d mile(s)' %
        city_visit_router_runner.max_walking_distance)
  print('Your schedule:')
  print(city_visit_best)
  print('Points left: %s' %
        ', '.join(point_left.name for point_left in points_left))

  print('Elapsed time %s' % (datetime.datetime.now() - start))


if __name__ == '__main__':
  main()
