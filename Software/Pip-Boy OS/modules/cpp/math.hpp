#pragma once
#include <math.h>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

struct Point3D
{
  float x, y, z;
  float *begin() { return &x; }
  float *end() { return &x + 3; }
};
struct Point2D
{
  float x, y;
  float *begin() { return &x; }
  float *end() { return &x + 2; }
};

struct Point2DInt
{
  int x, y;
  int *begin() { return &x; }
  int *end() { return &x + 2; }
};

struct Line2D
{
  int x1, y1, x2, y2;
};

struct Face
{
  unsigned int v1, v2, v3;
  unsigned int *begin() { return &v1; }
  unsigned int *end() { return &v1 + 3; }
};

// just declarations
float deg_to_rad(const float &deg);
void set_v(const Point3D &dim, Point3D &v);
void mv_v(const Point3D &pos, Point3D &v);
void rot_v(const Point3D &rot, Point3D &v);
Point3D sub_v(const Point3D &v1, const Point3D &v2);
Point3D cross_v(const Point3D &v1, const Point3D &v2);
Point3D norm(const Point3D &n);
Point3D div_v(const Point3D &v, const float &fact);
bool lines_equal(const Line2D &l1, const Line2D &l2, int eps2);
inline int dist2(int x1, int y1, int x2, int y2);
