#include "math.hpp"
#include "obj_loader.hpp"
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <utility>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

class WireframeRenderer
{
public:
  WireframeRenderer(int width, int height, float focal = 50.0f)
      : width(width), height(height), focal_l(focal), rot_z(0.0f), running(false)
  {
    camera = {0, 0, -10};
  }

  void load_model(const std::string &path)
  {
    obj = Obj(path);
    scale_obj_to_screen();
    original_v = obj.v;
  }
  void set_camera(float x, float y, float z)
  {
    camera = {x, y, z};
  }

  void set_rotation(float x, float y, float z)
  {
    rot = {deg_to_rad(x), deg_to_rad(y), deg_to_rad(z)};
  }

  // Lifecycle
  void start() { running = true; }
  void stop() { running = false; }

  bool is_running() const { return running; }

  std::vector<Line2D> render()
  {
    if (!running)
      return {};
    std::vector<Line2D> lines;
    Obj obj_new = obj;
    obj_new.v = original_v;

    rot_z += deg_to_rad(5.0f); // 1 degree per frame
    if (rot_z > M_PI * 2.0f)
      rot_z = 0.0f;

    Point3D rot_rad = {rot.x, rot.y + rot_z, rot.z};
    for (Point3D &v : obj_new.v)
    {
      rot_v(rot_rad, v);
    }

    std::vector<Point3D> camera_space_v;
    for (const Point3D &v : obj_new.v)
    {
      camera_space_v.push_back(sub_v(v, camera));
    }

    std::vector<Point2DInt> new_v;
    new_v.resize(camera_space_v.size());
    for (size_t i = 0; i < camera_space_v.size(); i++)
    {
      // std::cerr << "parsed vertex: " << camera_space_v[i].x << ", " << camera_space_v[i].y << ", " << camera_space_v[i].z << "\n";
      new_v[i] = conv_screen_space(camera_space_v[i], height, width, size_factor, focal_l);
    }

    for (const Face &f : obj_new.f)
    {
      // handle both 0-based and 1-based face indices
      auto convert_idx = [&](int idx) -> int
      {
        if (idx < 0)
          return -1;
        if ((size_t)idx < new_v.size())
          return idx; // 0-based OK
        if ((size_t)(idx - 1) < new_v.size())
          return idx - 1; // 1-based -> convert
        return -1;
      };

      int a = convert_idx(f.v1);
      int b = convert_idx(f.v2);
      int c = convert_idx(f.v3);
      if ((a < 0 || b < 0 || c < 0))
        continue;

      add_line(lines, new_v[a], new_v[b]);
      add_line(lines, new_v[b], new_v[c]);
      add_line(lines, new_v[c], new_v[a]);
    }
    return lines;
  }

private:
  int width, height;
  float focal_l;
  Point3D camera;
  Point3D rot = {0, 0, 0};
  float rot_z;
  bool running;
  const float size_factor = (width <= height) ? (float)width / 100.0f : (float)height / 100.0f;

  Obj obj;
  std::vector<Point3D> original_v;

  static Point2DInt conv_screen_space(const Point3D &vertex, const int &heights, const int &widths, const float &factor, const float &focal_l)
  {
    const float EPS_Z = 1e-4f;
    if (vertex.z <= EPS_Z)
      return {-1, -1};
    int sx = static_cast<int>(round(((vertex.x * focal_l / vertex.z) * factor) + (widths * 0.5f)));
    int sy = static_cast<int>(round(((vertex.y * focal_l / vertex.z) * factor) + (heights * 0.5f)));
    // std::cerr << "[conv] sx, sy: " << sx << "," << sy << "\n";
    return {sx, sy};
  }

  static void add_line(std::vector<Line2D> &out, const Point2DInt &a, const Point2DInt &b, int eps = 1)
  {
    Line2D new_line = {a.x, a.y, b.x, b.y};
    float eps2 = eps * eps;
    for (auto &l : out)
    {
      if (lines_equal(l, new_line, eps2))
        return; // skip duplicate
    }
    if (a.x > b.x || (a.x == b.x && a.y > b.y))
      std::swap(new_line.x1, new_line.x2), std::swap(new_line.y1, new_line.y2);

    out.push_back(new_line);
  }

  void scale_obj_to_screen()
  {
    // find the max dimension
    Point3D min = {INFINITY, INFINITY, INFINITY};
    Point3D max = {-INFINITY, -INFINITY, -INFINITY};
    for (const Point3D &v : obj.v)
    {
      min.x = std::min(min.x, v.x);
      min.y = std::min(min.y, v.y);
      min.z = std::min(min.z, v.z);

      max.x = std::max(max.x, v.x);
      max.y = std::max(max.y, v.y);
      max.z = std::max(max.z, v.z);
    }
    Point3D dim = sub_v(max, min);
    float max_dim = std::max({dim.x, dim.y, dim.z});
    if (max_dim < 1e-6f)
      return;                             // avoid div by zero
    float scale_factor = 20.0f / max_dim; // scale to fit in a 20x20x20 box
    for (Point3D &v : obj.v)
    {
      v.x *= scale_factor;
      v.y *= scale_factor;
      v.z *= scale_factor;
    }
  }
};

// PyBind11 module
PYBIND11_MODULE(wireframe, m)
{
  py::class_<Line2D>(m, "Line2D")
      .def_readonly("x1", &Line2D::x1)
      .def_readonly("y1", &Line2D::y1)
      .def_readonly("x2", &Line2D::x2)
      .def_readonly("y2", &Line2D::y2);

  py::class_<WireframeRenderer>(m, "WireframeRenderer")
      .def(py::init<int, int, float>())
      .def("load_model", &WireframeRenderer::load_model)
      .def("set_camera", &WireframeRenderer::set_camera)
      .def("set_rotation", &WireframeRenderer::set_rotation)
      .def("start", &WireframeRenderer::start)
      .def("stop", &WireframeRenderer::stop)
      .def("is_running", &WireframeRenderer::is_running)
      .def("render", &WireframeRenderer::render);
}