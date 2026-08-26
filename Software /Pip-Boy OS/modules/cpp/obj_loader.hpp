#pragma once
#include "math.hpp"
#include <array>
#include <string>
#include <vector>
#include <math.h>

class Obj
{
public:
  Obj() = default;
  Obj(const std::string &file_path);
  std::string name;
  std::vector<Point3D> v;
  std::vector<Face> f;

private:
  void parse_file(const std::string &file_path);
};