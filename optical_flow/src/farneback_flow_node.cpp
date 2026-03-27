#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

#include <cv_bridge/cv_bridge.h>
#include <opencv2/imgproc.hpp>
#include <opencv2/video.hpp>

using std::placeholders::_1;

class FarnebackFlowNode : public rclcpp::Node {
public:
  FarnebackFlowNode() : Node("farneback_optical_flow") {
    declare_parameter<std::string>("image_topic", "/camera/image_raw");
    declare_parameter<std::string>("output_topic", "/optflow/twist");
    declare_parameter<std::string>("frame_id", "base_link");

    // Placeholder scale (tune later). Converts px/s to "m/s-like" output.
    declare_parameter<double>("flow_to_mps_scale", 0.002);
    declare_parameter<int>("roi_margin_px", 40);

    // Farneback params
    declare_parameter<double>("pyr_scale", 0.5);
    declare_parameter<int>("levels", 3);
    declare_parameter<int>("winsize", 15);
    declare_parameter<int>("iterations", 3);
    declare_parameter<int>("poly_n", 5);
    declare_parameter<double>("poly_sigma", 1.2);
    declare_parameter<int>("flags", 0);

    image_topic_ = get_parameter("image_topic").as_string();
    output_topic_ = get_parameter("output_topic").as_string();
    frame_id_ = get_parameter("frame_id").as_string();
    scale_ = get_parameter("flow_to_mps_scale").as_double();
    roi_margin_px_ = get_parameter("roi_margin_px").as_int();

    pyr_scale_ = get_parameter("pyr_scale").as_double();
    levels_ = get_parameter("levels").as_int();
    winsize_ = get_parameter("winsize").as_int();
    iterations_ = get_parameter("iterations").as_int();
    poly_n_ = get_parameter("poly_n").as_int();
    poly_sigma_ = get_parameter("poly_sigma").as_double();
    flags_ = get_parameter("flags").as_int();

    pub_ = create_publisher<geometry_msgs::msg::TwistStamped>(output_topic_, 10);
    sub_ = create_subscription<sensor_msgs::msg::Image>(
      image_topic_, rclcpp::SensorDataQoS(),
      std::bind(&FarnebackFlowNode::on_image, this, _1));

    RCLCPP_INFO(get_logger(), "Subscribed: %s", image_topic_.c_str());
    RCLCPP_INFO(get_logger(), "Publishing: %s", output_topic_.c_str());
  }

private:
  void on_image(const sensor_msgs::msg::Image::SharedPtr msg) {
    cv_bridge::CvImageConstPtr cv_ptr;
    try {
      // Force mono8 for optical flow
      cv_ptr = cv_bridge::toCvShare(msg, "mono8");
    } catch (const cv_bridge::Exception &e) {
      RCLCPP_ERROR(get_logger(), "cv_bridge: %s", e.what());
      return;
    }

    const cv::Mat& gray = cv_ptr->image;

    if (prev_gray_.empty()) {
      prev_gray_ = gray.clone();
      prev_stamp_ = msg->header.stamp;
      return;
    }

    rclcpp::Time t_now(msg->header.stamp);
    rclcpp::Time t_prev(prev_stamp_);
    double dt = (t_now - t_prev).seconds();
    if (dt <= 1e-6) dt = 1.0 / 30.0;

    cv::Mat flow; // CV_32FC2
    cv::calcOpticalFlowFarneback(
      prev_gray_, gray, flow,
      pyr_scale_, levels_, winsize_, iterations_, poly_n_, poly_sigma_, flags_);

    int w = flow.cols, h = flow.rows;
    int m = std::max(0, roi_margin_px_);
    int x0 = m, y0 = m, x1 = w - m, y1 = h - m;
    if (x1 <= x0 + 1 || y1 <= y0 + 1) { x0 = 0; y0 = 0; x1 = w; y1 = h; }

    cv::Rect roi(x0, y0, x1 - x0, y1 - y0);
    cv::Scalar mean_flow = cv::mean(flow(roi));
    double mean_u = mean_flow[0]; // px/frame in x (right)
    double mean_v = mean_flow[1]; // px/frame in y (down)

    double u_px_s = mean_u / dt;
    double v_px_s = mean_v / dt;

    // Output convention (tunable later):
    // body y (right) ~ image u
    // body x (forward) ~ -image v  (depends on camera mount; placeholder)
    double vx = (-v_px_s) * scale_;
    double vy = ( u_px_s) * scale_;

    geometry_msgs::msg::TwistStamped out;
    out.header.stamp = msg->header.stamp;
    out.header.frame_id = frame_id_;
    out.twist.linear.x = vx;
    out.twist.linear.y = vy;
    out.twist.linear.z = 0.0;
    out.twist.angular.z = 0.0;

    pub_->publish(out);

    prev_gray_ = gray.clone();
    prev_stamp_ = msg->header.stamp;
  }

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr pub_;

  std::string image_topic_, output_topic_, frame_id_;
  double scale_;
  int roi_margin_px_;

  double pyr_scale_;
  int levels_, winsize_, iterations_, poly_n_, flags_;
  double poly_sigma_;

  cv::Mat prev_gray_;
  builtin_interfaces::msg::Time prev_stamp_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FarnebackFlowNode>());
  rclcpp::shutdown();
  return 0;
}
