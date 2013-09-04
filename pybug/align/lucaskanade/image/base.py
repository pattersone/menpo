from scipy.linalg import norm
import numpy as np
from pybug.warp.base import scipy_warp
from pybug.align.lucaskanade.base import LucasKanade


class ImageLucasKanade(LucasKanade):

    def __init__(self, template, residual, transform,
                 warp=scipy_warp, optimisation=('GN',), eps=10 ** -6):
        super(ImageLucasKanade, self).__init__(
            residual, transform,
            warp, optimisation, eps)
        # in image alignment, we align a template image to the target image
        self.template = template

        # pre-compute
        self._precompute()


class ImageForwardAdditive(ImageLucasKanade):

    def _align(self, max_iters=30):
        # Initial error > eps
        error = self.eps + 1

        # Forward Additive Algorithm
        while self.n_iters < (max_iters - 1) and error > self.eps:
            # Compute warped image with current parameters
            IWxp = self._warp(self.image, self.template,
                              self.optimal_transform)

            # Compute the Jacobian of the warp
            dW_dp = self.optimal_transform.jacobian(
                self.template.mask.true_indices)

            # TODO: rename kwarg "forward" to "forward_additive"
            # Compute steepest descent images, VI_dW_dp
            VI_dW_dp = self.residual.steepest_descent_images(
                self.image, dW_dp, forward=(self.template,
                                            self.optimal_transform,
                                            self._warp))

            # Compute Hessian
            self._H = self.residual.calculate_hessian(VI_dW_dp)

            # Compute steepest descent parameter updates
            sd_delta_p = self.residual.steepest_descent_update(
                VI_dW_dp, self.template, IWxp)

            # Compute gradient descent parameter updates
            delta_p = np.real(self._calculate_delta_p(sd_delta_p))

            # Update warp parameters
            new_params = self.optimal_transform.as_vector() + delta_p
            self.transforms.append(
                self.initial_transform.from_vector(new_params))

            # Test convergence
            error = np.abs(norm(delta_p))

        return self.optimal_transform


class ImageForwardCompositional(ImageLucasKanade):

    def _precompute(self):
        r"""
        The forward compositional algorithm pre-computes the Jacobian of the
        warp. This is set as an attribute on the class.
        """
        # Compute the Jacobian of the warp
        self._dW_dp = self.initial_transform.jacobian(
            self.template.mask.true_indices)

    def _align(self, max_iters=30):
        # Initial error > eps
        error = self.eps + 1

        # Forward Compositional Algorithm
        while self.n_iters < (max_iters - 1) and error > self.eps:
            # Compute warped image with current parameters
            IWxp = self._warp(self.image, self.template,
                              self.optimal_transform)

            # TODO: add "forward_compositional" kwarg with options
            # In the forward compositional algorithm there are two different
            # ways of computing the steepest descent images:
            #   1. V[I(x)](W(x,p)) * dW/dx * dW/dp
            #   2. V[I(W(x,p))] * dW/dp -> this is what is currently used
            # Compute steepest descent images, VI_dW_dp
            VI_dW_dp = self.residual.steepest_descent_images(IWxp,
                                                             self._dW_dp)

            # Compute Hessian
            self._H = self.residual.calculate_hessian(VI_dW_dp)

            # Compute steepest descent parameter updates
            sd_delta_p = self.residual.steepest_descent_update(
                VI_dW_dp, self.template, IWxp)

            # Compute gradient descent parameter updates
            delta_p = np.real(self._calculate_delta_p(sd_delta_p))

            # Update warp parameters
            delta_p_transform = self.initial_transform.from_vector(delta_p)
            self.transforms.append(
                self.optimal_transform.compose(delta_p_transform))

            # Test convergence
            error = np.abs(norm(delta_p))

        return self.optimal_transform


class ImageInverseCompositional(ImageLucasKanade):

    def _precompute(self):
        r"""
        The Inverse Compositional algorithm pre-computes the Jacobian of the
        warp, the steepest descent images and the Hessian. These are all
        stored as attributes on the class.
        """
        # Compute the Jacobian of the warp
        dW_dp = self.initial_transform.jacobian(
            self.template.mask.true_indices)

        # Compute steepest descent images, VT_dW_dp
        self._VT_dW_dp = self.residual.steepest_descent_images(
            self.template, dW_dp)

        # Compute Hessian
        self._H = self.residual.calculate_hessian(self._VT_dW_dp)

    def _align(self, max_iters=30):
        # Initial error > eps
        error = self.eps + 1

        # Baker-Matthews, Inverse Compositional Algorithm
        while self.n_iters < (max_iters - 1) and error > self.eps:
            # Compute warped image with current parameters
            IWxp = self._warp(self.image, self.template,
                              self.optimal_transform)

            # Compute steepest descent parameter updates
            sd_delta_p = self.residual.steepest_descent_update(
                self._VT_dW_dp, IWxp, self.template)

            # Compute gradient descent parameter updates
            delta_p = np.real(self._calculate_delta_p(sd_delta_p))

            # Update warp parameters
            delta_p_transform = self.initial_transform.from_vector(delta_p)
            self.transforms.append(
                self.optimal_transform.compose(delta_p_transform.inverse))

            # Test convergence
            error = np.abs(norm(delta_p))

        return self.optimal_transform