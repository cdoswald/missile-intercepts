"""Unit tests for missile_classes.py."""

# Import packages
import inspect
import os
import sys

# Import local modules
script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)
import missile_classes as missiles

# Define tests
def test_BallisticMissile_init():
    """Test that BallisticMissile class can be instantiated without arguments."""
    errors_list = []
    try:
        missile = missiles.BallisticMissile()
        if not vars(missile):
            errors_list.append(
                'Instantiated BallisticMissile object does not have attributes.'
            )
    except Exception as error:
        errors_list.append(
            'BallisticMissile class could not be instantiated for the '+
            f'following reason: \n\t"{error}"'
        )
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))
