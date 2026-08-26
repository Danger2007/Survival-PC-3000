#include "math.hpp"
#include <cmath>

float deg_to_rad(const float &deg) { return deg * (M_PI / 180.0f); }

void mv_v(const Point3D &pos, Point3D &v)
{
  v.x -= pos.x;
  v.y -= pos.y;
  v.z -= pos.z;
}

void rot_v(const Point3D &rot, Point3D &v)
{
  const double cx = cos(rot.x), sx = sin(rot.x);
  const double cy = cos(rot.y), sy = sin(rot.y);
  const double cz = cos(rot.z), sz = sin(rot.z);

  const double x = v.x;
  const double y = v.y;
  const double z = v.z;

  // rotate around Y
  const double x1 = x * cy + z * sy;
  const double z1 = -x * sy + z * cy;

  // rotate around X (use z1)
  const double y2 = y * cx - z1 * sx;
  const double z2 = y * sx + z1 * cx;

  // rotate around Z (use x1, y2)
  const double x3 = x1 * cz - y2 * sz;
  const double y3 = x1 * sz + y2 * cz;

  v.x = static_cast<float>(x3);
  v.y = static_cast<float>(y3);
  v.z = static_cast<float>(z2);
}

Point3D sub_v(const Point3D &v1, const Point3D &v2)
{
  return {v1.x - v2.x, v1.y - v2.y, v1.z - v2.z};
}

Point3D cross_v(const Point3D &v1, const Point3D &v2)
{
  return {
      (v1.y * v2.z - v2.z * v1.y),
      (v1.z * v2.x - v1.x * v2.z),
      (v1.x * v2.y - v1.y * v2.x)};
}

Point3D div_v(const Point3D &v, const float &fact)
{
  return {v.x / fact, v.y / fact, v.z / fact};
}

Point3D norm(const Point3D &n)
{
  float len = sqrt(n.x * n.x + n.y * n.y + n.z * n.z);
  if (len == 0.0f)
    return {0, 0, 0};
  return div_v(n, len);
}


inline int dist2(int x1, int y1, int x2, int y2)
{
  int dx = x1 - x2;
  int dy = y1 - y2;
  return dx * dx + dy * dy;
}

bool lines_equal(const Line2D &l1, const Line2D &l2, int eps2)
{
  return (dist2(l1.x1, l1.y1, l2.x1, l2.y1) <= eps2 && dist2(l1.x2, l1.y2, l2.x2, l2.y2) <= eps2) ||
         (dist2(l1.x1, l1.y1, l2.x2, l2.y2) <= eps2 && dist2(l1.x2, l1.y2, l2.x1, l2.y1) <= eps2);
}
