# -*- coding: utf-8 -*-

import math
import numpy as np
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

MU_KMS = {
    '500@10': 1.32712440018e11,
    '500@0':  1.32712440018e11,
    '500@399': 398600.4418,
}


class GnrCustomWebPage(object):
    js_requires = 'trajectory'

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main', padding='5px')

        top = bc.contentPane(region='top')
        fb = top.formlet(datapath='.parameters', cols=4)
        fb.dbselect(value='^.asteroid_id', table='astro.asteroid',
                    auxColumns='$neo_reference_id',
                    colspan=2,
                    condition='$has_ephemeris=:v', condition_v=True,
                    hasDownArrow=True,
                    lbl='Asteroid', validate_notnull=True, width='20em')
        fb.dbselect(value='^.fetch_id', table='astro.asteroid_fetch',
                    condition='$asteroid_id=:aid',
                    condition_aid='^.asteroid_id',
                    rowcaption='$caption',
                    colspan=2,
                    auxColumns='$fetched_at,$ref_system,$center,$step_value,$step_unit,$out_units',
                    hasDownArrow=True,
                    lbl='Fetch', validate_notnull=True, width='28em')
        fb.button('Disegna sample',
                  action="trajectory.plotSamples(p);",
                  p='=main.points')
        fb.button('Calcola Kepler',
                  action="trajectory.plotOrbit(o);",
                  o='=main.orbit')
        fb.button('Anima',
                  action="trajectory.toggleAnimation(p, o, m);",
                  p='=main.points', o='=main.orbit', m='=main.mu')
        fb.div(value='^main.current_v', lbl='|v|',
               readOnly=True, width='10em',
               font_family='monospace')
        bc.dataRpc('main.points', self.get_trajectory,
                   fetch_id='^.parameters.fetch_id',
                   _if='fetch_id',
                   _lockScreen=True)
        bc.dataRpc('main.orbit', self.get_orbit,
                   fetch_id='^.parameters.fetch_id',
                   _if='fetch_id',
                   max_radius=384400000.0,
                   _lockScreen=True)
        bc.dataRpc('main.mu', self.get_mu,
                   fetch_id='^.parameters.fetch_id',
                   _if='fetch_id')
        grid = bc.contentPane(region='bottom', height='200px').quickGrid(
            value='^main.points', datamode='attr', height='100%')
        grid.column(name='Point', field='_pkey', width='6em')
        grid.column(name='X', field='x', width='14em',
                    dtype='N', format='#,###.000000')
        grid.column(name='Y', field='y', width='14em',
                    dtype='N', format='#,###.000000')
        grid.column(name='Z', field='z', width='14em',
                    dtype='N', format='#,###.000000')

        center = bc.contentPane(region='center')
        center.div(nodeId='trajectory_canvas',
                   background_color='#000010',
                   width='100%', height='100%')

        bc.dataController(
            "trajectory.init('trajectory_canvas');", _onBuilt=True)

    @public_method
    def get_trajectory(self, fetch_id=None, **kwargs):
        result = Bag()
        if not fetch_id:
            return result
        rows = self.db.table('astro.asteroid_ephemeris').query(
            where='$fetch_id=:fid', fid=fetch_id,
            columns='$x,$y,$z,$vx,$vy,$vz',
            order_by='$epoch_jd').fetch()
        for i, row in enumerate(rows):
            result.setItem(f'p_{i}', None,
                           x=float(row['x']),
                           y=float(row['y']),
                           z=float(row['z']),
                           vx=float(row['vx'] or 0),
                           vy=float(row['vy'] or 0),
                           vz=float(row['vz'] or 0))
        return result

    def mukms(self, v):
        return MU_KMS.get(v, MU_KMS['500@10'])

    @public_method
    def get_mu(self, fetch_id=None, **kwargs):
        if not fetch_id:
            return None
        center = self.db.table('astro.asteroid_fetch').readColumns(
            where='$id=:fid', fid=fetch_id, columns='$center')
        return self.mukms(center)

    @public_method
    def get_orbit(self, fetch_id=None, n_points=400,
                  max_radius=None, **kwargs):
        result = Bag()
        if not fetch_id:
            return result
        rows = self.db.table('astro.asteroid_ephemeris').query(
            where='$fetch_id=:fid', fid=fetch_id,
            columns='$x,$y,$z',
            order_by='$epoch_jd').fetch()
        if len(rows) < 5:
            return result
        for i, p in enumerate(self._conic_points(rows, max_radius, n_points)):
            result.setItem(f'c_{i}', None, x=p[0], y=p[1], z=p[2])
        return result

    def _conic_points(self, rows, max_radius, n_points, n_theta=2000):
        """Fit di una conica generica passante per 5 sample equispaziati.

        Equazione generale 2D: Ax² + Bxy + Cy² + Dx + Ey + F = 0
        Con F=-1, restano 5 incognite: 5 punti → soluzione unica.

        Pipeline:
          1. SVD sui sample per trovare il piano migliore
          2. Proietta i 5 punti in 2D nel piano
          3. Normalizza per condizionamento numerico
          4. Risolve il sistema lineare 5×5
          5. Trova il centro della conica
          6. Sweep θ attorno al centro, traccia il ramo passante per i sample
          7. Classifica via discriminante B²-4AC
        """
        idx = np.linspace(0, len(rows) - 1, 5, dtype=int)
        sampled = [rows[i] for i in idx]
        pts_3d = np.array([[float(r['x']), float(r['y']), float(r['z'])]
                           for r in sampled])
        centroid = pts_3d.mean(axis=0)
        centered = pts_3d - centroid
        _, _, Vt = np.linalg.svd(centered, full_matrices=False)
        e_x, e_y = Vt[0], Vt[1]

        pts_2d_raw = np.column_stack([centered @ e_x, centered @ e_y])
        scale_2d = float(np.max(np.abs(pts_2d_raw)))
        if scale_2d < 1e-12:
            return []
        pts_2d = pts_2d_raw / scale_2d

        M = np.column_stack([pts_2d[:, 0]**2,
                             pts_2d[:, 0]*pts_2d[:, 1],
                             pts_2d[:, 1]**2,
                             pts_2d[:, 0],
                             pts_2d[:, 1]])
        rhs = np.ones(len(pts_2d))
        coeffs, *_ = np.linalg.lstsq(M, rhs, rcond=None)
        A, B, C, D, E = (float(c) for c in coeffs)
        F = -1.0

        discriminant = B*B - 4*A*C
        center_mat = np.array([[2*A, B], [B, 2*C]])
        if abs(np.linalg.det(center_mat)) < 1e-15:
            print('[trajectory] center matrix singular — abort')
            return []
        xc, yc = np.linalg.solve(center_mat, np.array([-D, -E]))
        Fp = A*xc*xc + B*xc*yc + C*yc*yc + D*xc + E*yc + F

        xs = pts_2d[0, 0] - xc
        ys = pts_2d[0, 1] - yc
        th_start = math.atan2(ys, xs)
        d_th = 2*math.pi / n_theta

        def point_at(th):
            cs, sn = math.cos(th), math.sin(th)
            denom = A*cs*cs + B*cs*sn + C*sn*sn
            if abs(denom) < 1e-18:
                return None
            rsq = -Fp / denom
            if rsq <= 0 or not math.isfinite(rsq):
                return None
            r = math.sqrt(rsq)
            xp = (xc + r*cs) * scale_2d
            yp = (yc + r*sn) * scale_2d
            pos3 = centroid + xp*e_x + yp*e_y
            if max_radius and float(np.linalg.norm(pos3)) > max_radius:
                return None
            return [float(pos3[0]), float(pos3[1]), float(pos3[2])]

        def trace(sign):
            out = []
            for i in range(1, n_theta + 1):
                th = th_start + sign * i * d_th
                p = point_at(th)
                if p is None:
                    break
                out.append(p)
                if sign * i * d_th >= 2*math.pi:
                    break
            return out

        forward = trace(+1)
        backward = trace(-1)
        start = point_at(th_start)
        pts = list(reversed(backward))
        if start is not None:
            pts.append(start)
        pts.extend(forward)

        kind = 'hyperbola' if discriminant > 0 \
            else 'ellipse' if discriminant < 0 \
            else 'parabola'
        print(f'[trajectory] conic fit: {kind} '
              f'(B²-4AC={discriminant:.3e}, points={len(pts)})')

        if len(pts) > n_points:
            step = len(pts) / n_points
            pts = [pts[int(i*step)] for i in range(n_points)]
        return pts
