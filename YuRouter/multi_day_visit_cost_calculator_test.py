import unittest

import Yusi
from Yusi.YuRouter.day_visit_cost_calculator_interface import DayVisitCostCalculatorInterface,\
  DayVisitCostCalculatorGeneratorInterface
from Yusi.YuRouter.multi_day_visit_cost_calculator import MultiDayVisitCostCalculatorGenerator
from Yusi.YuPoint.city_visit import DayVisitParametersInterface
from Yusi.YuPoint.point import PointInterface


class MockPoint(PointInterface):
  pass


class MockDayVisitParameters(DayVisitParametersInterface):
  pass


# NOTE(igushev): We imitate time constrains by cost constrains in this class.
class MockDayVisitCostCalculator(DayVisitCostCalculatorInterface):
  
  def __init__(self, costs, finalization_cost, no_push_cost, max_cost):
    self.costs = costs
    self.finalization_cost = finalization_cost
    self.no_push_cost = no_push_cost
    self.max_cost = max_cost
    self.cost = 0
    self.pos = 0
    self.points_left = []
    
  def PushPoint(self, point):
    assert isinstance(point, MockPoint)
    assert self.pos <= len(self.costs)
    if (self.points_left or
        self.cost + self.costs[self.pos] + self.finalization_cost >
        self.max_cost):
      self.cost += self.no_push_cost
      self.points_left.append(point)
      return False
    self.cost += self.costs[self.pos]
    self.pos += 1
    return True
    
  def FinalizedCost(self):
    return self.cost + self.finalization_cost

  def FinalizedDayVisit(self):
    return self

  def GetPointsLeft(self):
    return self.points_left

  def Pos(self):
    assert self.pos <= len(self.costs)
    return self.pos


class MockDayVisitCostCalculatorGenerator(
    DayVisitCostCalculatorGeneratorInterface):
  
  def __init__(self, costs, finalization_cost, no_push_cost, max_cost):
    self.costs = costs
    self.finalization_cost = finalization_cost
    self.no_push_cost = no_push_cost
    self.max_cost = max_cost

  def Generate(self, day_visit_parameters):
    assert isinstance(day_visit_parameters, MockDayVisitParameters)
    return MockDayVisitCostCalculator(
        self.costs, self.finalization_cost, self.no_push_cost, self.max_cost)


class MultiDayVisitCostCalculatorTest(unittest.TestCase):
  
  def testBothPushed(self):
    calculator_generator_1 = (
        MockDayVisitCostCalculatorGenerator([3, 4], 1, 100, 9))
    calculator_generator_2 = (
        MockDayVisitCostCalculatorGenerator([1, 6], 2, 100, 10))
    calculator = (
        MultiDayVisitCostCalculatorGenerator(
            [calculator_generator_1, calculator_generator_2]).
        Generate(MockDayVisitParameters()))
    calculator_1, calculator_2 = calculator.calculators

    # Empty calculator.
    # First one is better.
    self.assertEqual(0, calculator_1.Pos())
    self.assertEqual(0, calculator_2.Pos())
    self.assertEqual([], calculator_1.GetPointsLeft())
    self.assertEqual([], calculator_2.GetPointsLeft())
    self.assertEqual(1, calculator_1.FinalizedCost())
    self.assertEqual(2, calculator_2.FinalizedCost())
    self.assertEqual(1, calculator.FinalizedCost())
    self.assertIs(calculator_1, calculator.FinalizedDayVisit())
    self.assertEqual([], calculator.GetPointsLeft())

    # Pushing first point.
    # Second one is better.
    self.assertTrue(calculator.PushPoint(MockPoint()))
    self.assertEqual(1, calculator_1.Pos())
    self.assertEqual(1, calculator_2.Pos())
    self.assertEqual([], calculator_1.GetPointsLeft())
    self.assertEqual([], calculator_2.GetPointsLeft())
    self.assertEqual(4, calculator_1.FinalizedCost())
    self.assertEqual(3, calculator_2.FinalizedCost())
    self.assertEqual(3, calculator.FinalizedCost())
    self.assertIs(calculator_2, calculator.FinalizedDayVisit())
    self.assertEqual([], calculator.GetPointsLeft())

    # Pushing second point.
    # First one again better.
    self.assertTrue(calculator.PushPoint(MockPoint()))
    self.assertEqual(2, calculator_1.Pos())
    self.assertEqual(2, calculator_2.Pos())
    self.assertEqual([], calculator_1.GetPointsLeft())
    self.assertEqual([], calculator_2.GetPointsLeft())
    self.assertEqual(8, calculator_1.FinalizedCost())
    self.assertEqual(9, calculator_2.FinalizedCost())
    self.assertEqual(8, calculator.FinalizedCost())
    self.assertIs(calculator_1, calculator.FinalizedDayVisit())
    self.assertEqual([], calculator.GetPointsLeft())

  def testOnePushed(self):
    calculator_generator_1 = (
        MockDayVisitCostCalculatorGenerator([3, 4], 1, 100, 7.5))
    calculator_generator_2 = (
        MockDayVisitCostCalculatorGenerator([1, 6], 2, 100, 10))
    calculator = (
        MultiDayVisitCostCalculatorGenerator(
            [calculator_generator_1, calculator_generator_2]).
        Generate(MockDayVisitParameters()))
    calculator_1, calculator_2 = calculator.calculators

    # See testGeneral.
    # Empty calculator.
    # First one is better.
    # Pushing first point.
    # Second one is better.
    self.assertTrue(calculator.PushPoint(MockPoint()))

    # Pushing second point.
    # First one can't be finalized.
    # Second one is better.
    second_point = MockPoint()
    self.assertTrue(calculator.PushPoint(second_point))
    self.assertEqual(1, calculator_1.Pos())
    self.assertEqual(2, calculator_2.Pos())
    self.assertEqual([second_point], calculator_1.GetPointsLeft())
    self.assertEqual([], calculator_2.GetPointsLeft())
    self.assertEqual(104, calculator_1.FinalizedCost())
    self.assertEqual(9, calculator_2.FinalizedCost())
    self.assertEqual(9, calculator.FinalizedCost())
    self.assertIs(calculator_2, calculator.FinalizedDayVisit())
    self.assertEqual([], calculator.GetPointsLeft())

  def testNonePushed(self):
    calculator_generator_1 = (
        MockDayVisitCostCalculatorGenerator([3, 4], 1, 100, 7.5))
    calculator_generator_2 = (
        MockDayVisitCostCalculatorGenerator([1, 6], 2, 100, 8))
    calculator = (
        MultiDayVisitCostCalculatorGenerator(
            [calculator_generator_1, calculator_generator_2]).
        Generate(MockDayVisitParameters()))
    calculator_1, calculator_2 = calculator.calculators

    # See testGeneral.
    # Empty calculator.
    # First one is better.
    # Pushing first point.
    # Second one is better.
    self.assertTrue(calculator.PushPoint(MockPoint()))

    # Pushing second point.
    # None can be finalized.
    second_point = MockPoint()
    self.assertFalse(calculator.PushPoint(second_point))
    self.assertEqual(1, calculator_1.Pos())
    self.assertEqual(1, calculator_2.Pos())
    self.assertEqual([second_point], calculator_1.GetPointsLeft())
    self.assertEqual([second_point], calculator_2.GetPointsLeft())
    self.assertEqual(104, calculator_1.FinalizedCost())
    self.assertEqual(103, calculator_2.FinalizedCost())
    self.assertEqual(103, calculator.FinalizedCost())
    self.assertEqual(calculator_2, calculator.FinalizedDayVisit())
    self.assertEqual([second_point], calculator.GetPointsLeft())


if __name__ == '__main__':
    unittest.main()
